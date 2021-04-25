import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from footgram import settings
from users.models import User

from .forms import RecipeForm
from .models import (Favorites, Ingredient, IngredientItem, Recipe, ShopList,
                     Subscribe, Tag)
from .utils import get_tag


def index(request):
    tags_values = request.GET.getlist('filters')
    recipe = Recipe.objects.all()
    if tags_values:
        recipe = recipe.filter(tag__title__in=tags_values).all()
    tags = Tag.objects.all()
    paginator = Paginator(recipe, settings.RECIPES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
    }
    return render(request, 'index.html', context)


@login_required()
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES)
    tags = Tag.objects.all()
    ingredient_names = request.POST.getlist('nameIngredient')
    ingredient_units = request.POST.getlist('unitsIngredient')
    amount = request.POST.getlist('valueIngredient')
    tags_post = get_tag(request)
    if not form.is_valid():
        context = {'form': form, 'tags': tags}
        return render(request, 'new_recipe.html', context)
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    products_num = len(ingredient_names)
    ingredients = []
    for i in range(products_num):
        product = Ingredient.objects.get(
            title=ingredient_names[i],
            dimension=ingredient_units[i]
        )
        ingredients.append(
            IngredientItem(recipe=recipe, ingredients=product, count=amount[i])
        )
    IngredientItem.objects.bulk_create(ingredients)
    for i in tags_post:
        tag = get_object_or_404(Tag, title=i)
        recipe.tag.add(tag)
    form.save_m2m()
    return redirect('index')


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)


def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return render(request, 'forbidden.html')
    ingredients = recipe.ingredients.all()
    tags = Tag.objects.all()
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe
    )
    tags_post = get_tag(request)
    ingredient_names = request.POST.getlist('nameIngredient')
    ingredient_units = request.POST.getlist('unitsIngredient')
    amount = request.POST.getlist('valueIngredient')
    context = {'form': form, 'tags': tags, 'ingredients': ingredients,
               'recipe': recipe}
    if not form.is_valid():
        return render(request, 'edit_recipe.html', context)
    form.save()
    products_num = len(ingredient_names)
    new_ingredients = []
    IngredientItem.objects.filter(recipe__id=recipe_id).delete()
    for i in range(products_num):
        product = Ingredient.objects.get(title=ingredient_names[i],
                                         dimension=ingredient_units[i])
        new_ingredients.append(
            IngredientItem(recipe=recipe, ingredients=product, count=amount[i])
        )
    IngredientItem.objects.bulk_create(new_ingredients)
    recipe.tag.clear()
    for i in tags_post:
        tag = get_object_or_404(Tag, title=i)
        recipe.tag.add(tag)
    return redirect('index')


@login_required()
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    author = recipe.author
    if user != author:
        return render(request, 'forbidden.html')
    recipe.delete()
    return redirect(index)


@login_required()
def get_ingredients(request):
    text = request.GET.get('query').rstrip('/')
    data = []
    ingredients = Ingredient.objects.filter(
        title__startswith=text).all()
    for ingredient in ingredients:
        data.append(
            {'title': ingredient.title, 'dimension': ingredient.dimension})
    return JsonResponse(data, safe=False)


@login_required()
def purchases_list(request):
    user = request.user
    my_shop_list = ShopList.objects.filter(user=user).first()
    recipes = None
    if my_shop_list:
        recipes = my_shop_list.recipes.all()
    return render(
        request,
        template_name='shopList.html',
        context={'recipes': recipes}
    )


@require_http_methods('POST')
def purchases_add(request):
    recipe_id = json.loads(request.body).get('id')
    recipe = get_object_or_404(Recipe, id=recipe_id)
    shop_list, _ = ShopList.objects.get_or_create(user=request.user)
    shop_list.recipes.add(recipe)
    return JsonResponse({'success': True})


@require_http_methods('DELETE')
def purchases_delete(request, recipe_id):
    user = request.user
    shop_list, _ = ShopList.objects.get_or_create(user=user.id)
    current_recipe = get_object_or_404(Recipe, id=recipe_id)
    shop_list.recipes.remove(current_recipe)
    return JsonResponse({'success': True})


@login_required()
def purchases_delete_index(request, recipe_id):
    user = request.user
    shop_list, _ = ShopList.objects.get_or_create(user=user.id)
    current_recipe = get_object_or_404(Recipe, id=recipe_id)
    shop_list.recipes.remove(current_recipe)
    return redirect('purchases_list')


@login_required()
def purchases_download(request):
    shops = get_object_or_404(ShopList, user=request.user)
    recipes = shops.recipes.all()
    ingredients = IngredientItem.objects.filter(
        recipe__in=recipes).select_related('ingredients').values(
        'ingredients__title', 'ingredients__dimension').annotate(
        count=Sum('count')).all()
    header = 'Список покупок\n\n'

    for ingredient in ingredients:
        name = ingredient['ingredients__title']
        dimension = ingredient['ingredients__dimension']
        count = ingredient['count']
        header += f'{name} ({dimension}) - {count}\n'

    response = HttpResponse(header, content_type='text/txt')
    response['Content-Disposition'] = 'attachment; filename="purchases.txt"'
    return response


@login_required()
def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipe = Recipe.objects.select_related('author').filter(
        author=author).all()
    tags_values = request.GET.getlist('filters')
    if tags_values:
        recipe = recipe.filter(tag__title__in=tags_values).all()
    tags = Tag.objects.all()
    paginator = Paginator(recipe, settings.RECIPES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow = request.user.is_authenticated and request.user != author

    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
        'author': author,
        'follow': follow,
    }
    return render(request, 'authorRecipe.html', context)


@login_required()
def follow(request):
    authors_list = Subscribe.objects.select_related('user', 'author').filter(
        user=request.user
    )
    paginator = Paginator(authors_list, settings.RECIPES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'myFollow.html', context)


@login_required()
@require_http_methods('POST')
def subscription(request):
    json_data = json.loads(request.body.decode())
    author_id = json_data.get('id', None)
    if not author_id:
        return JsonResponse({'success': False})
    author = get_object_or_404(User, id=author_id)
    _, create = Subscribe.objects.get_or_create(
        user=request.user,
        author=author
    )
    if create:
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required()
@require_http_methods('DELETE')
def delete_subscription(request, author_id):
    data = {'success': 'true'}
    follow = get_object_or_404(
        Subscribe,
        user__username=request.user.username,
        author__id=author_id
    )
    if not follow:
        data['success'] = 'false'
    follow.delete()
    return JsonResponse(data)


@login_required()
def favorite_index(request, ):
    tags_values = request.GET.getlist('filters')
    recipe_list = Recipe.objects.filter(
        fans__user_id=request.user.id).all()
    if tags_values:
        recipe_list = recipe_list.filter(
            tag__title__in=tags_values
        )
    tags = Tag.objects.all()
    paginator = Paginator(recipe_list, settings.RECIPES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator, 'tags': tags}
    return render(request, 'favorite.html', context)


@login_required()
def favorites_add(request):
    json_data = json.loads(request.body.decode())
    recipe_id = json_data.get('id')
    if not recipe_id:
        return JsonResponse({'success': False})
    recipe = get_object_or_404(Recipe, id=recipe_id)
    _, create = Favorites.objects.get_or_create(
        user=request.user, recipe=recipe
    )
    if create:
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required()
def favorites_delete(request, recipe_id):
    recipe = get_object_or_404(
        Favorites, recipe=recipe_id, user=request.user
    )
    if recipe.delete():
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
