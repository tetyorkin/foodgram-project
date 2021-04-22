import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

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
        recipe = recipe.filter(tag__title__in=tags_values).distinct().all()
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


@login_required(login_url='accounts/login/')
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES)
    tags = Tag.objects.all()
    if not request.POST:
        context = {'form': form, 'tags': tags}
        return render(request, 'new_recipe.html', context)
    ingredient_names = request.POST.getlist('nameIngredient')
    ingredient_units = request.POST.getlist('unitsIngredient')
    amounts = request.POST.getlist('valueIngredient')
    tags_post = get_tag(request)
    if not tags_post:
        form.add_error('tag', 'Обязательное поле')
    if not ingredient_names:
        form.add_error('ingredient', 'Ингредиент не выбран')
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
            IngredientItem(recipe=recipe,
                           ingredients=product,
                           count=amounts[i])
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


@login_required(login_url='accounts/login/')
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'GET':
        form = RecipeForm(
            request.POST or None,
            files=request.FILES or None,
            instance=recipe
        )
        ingredients = recipe.ingredients.all()
        tags = Tag.objects.all()

        context = {
            'form': form,
            'recipe': recipe,
            'ingredients': ingredients,
            'tags': tags
        }
        return render(request, 'edit_recipe.html', context)
    if request.method == 'POST':
        user = request.user
        author = recipe.author
        if user != author:
            return render(request, 'forbidden.html')
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        tags = get_tag(request)
        ingredient_names = request.POST.getlist('nameIngredient')
        ingredient_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        if not tags:
            form.add_error('tag', 'Обязательное поле')
        if not ingredient_names:
            form.add_error('ingredient', 'Ингредиент не выбран')
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'edit_recipe.html', context)
        form.save()
        products_num = len(ingredient_names)
        new_ingredients = []
        IngredientItem.objects.filter(recipe__id=recipe_id).delete()
        for i in range(products_num):
            product = Ingredient.objects.get(title=ingredient_names[i],
                                             dimension=ingredient_units[i])
            new_ingredients.append(
                IngredientItem(recipe=recipe, ingredients=product,
                               count=amounts[i]))
        IngredientItem.objects.bulk_create(new_ingredients)
        tags = get_tag(request)
        recipe.tag.clear()
        for i in tags:
            tag = get_object_or_404(Tag, title=i)
            recipe.tag.add(tag)
        return redirect('index')


@login_required(login_url='accounts/login/')
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    author = recipe.author
    if user != author:
        return render(request, 'forbidden.html')
    recipe.delete()
    return redirect(index)


@login_required(login_url='accounts/login/')
def get_ingredients(request):
    text = request.GET.get('query').rstrip('/')
    data = []
    ingredients = Ingredient.objects.filter(
        title__startswith=text).all()
    for ingredient in ingredients:
        data.append(
            {'title': ingredient.title, 'dimension': ingredient.dimension})
    return JsonResponse(data, safe=False)


@login_required(login_url='accounts/login/')
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


def purchases_add(request):
    if request.method == 'POST':
        recipe_id = json.loads(request.body).get('id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shop_list = ShopList.objects.get_or_create(user=request.user)[0]
        shop_list.recipes.add(recipe)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def purchases_delete(request, recipe_id):
    if request.method == 'DELETE':
        user = request.user
        shop_list, _ = ShopList.objects.get_or_create(user=user.id)
        current_recipe = get_object_or_404(Recipe, id=recipe_id)
        shop_list.recipes.remove(current_recipe)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required(login_url='accounts/login/')
def purchases_delete_index(request, recipe_id):
    user = request.user
    shop_list, _ = ShopList.objects.get_or_create(user=user.id)
    current_recipe = get_object_or_404(Recipe, id=recipe_id)
    shop_list.recipes.remove(current_recipe)
    return redirect('purchases_list')


@login_required(login_url='accounts/login/')
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


@login_required(login_url='accounts/login/')
def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipe = Recipe.objects.select_related('author').filter(
        author=author).all()
    tags_values = request.GET.getlist('filters')
    if tags_values:
        recipe = recipe.filter(tag__title__in=tags_values).distinct().all()
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


@login_required(login_url='accounts/login/')
def follow(request):
    authors_list = Subscribe.objects.select_related('user', 'author').filter(
        user=request.user
    )
    paginator = Paginator(authors_list, settings.RECIPES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'myFollow.html', context)


@login_required(login_url='accounts/login/')
@require_POST
def subscription(request):
    json_data = json.loads(request.body.decode())
    author_id = json_data.get('id', None)
    if author_id is not None:
        author = get_object_or_404(User, id=author_id)
        _, create = Subscribe.objects.get_or_create(
            user=request.user,
            author=author
        )
        if create:
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    return JsonResponse({'success': False})


@login_required(login_url='accounts/login/')
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


@login_required(login_url='accounts/login/')
def favorite_index(request, ):
    tags_values = request.GET.getlist('filters')
    recipe_list = Recipe.objects.filter(
        fans__user_id=request.user.id).all()
    if tags_values:
        recipe_list = recipe_list.filter(
            tag__title__in=tags_values
        ).distinct()
    tags = Tag.objects.all()
    paginator = Paginator(recipe_list, settings.RECIPES_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator, 'tags': tags}
    return render(request, 'favorite.html', context)


@login_required(login_url='accounts/login/')
def favorites_add(request):
    json_data = json.loads(request.body.decode())
    recipe_id = json_data.get('id')
    if recipe_id:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        _, create = Favorites.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if create:
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    return JsonResponse({'success': False})


@login_required(login_url='accounts/login/')
def favorites_delete(request, recipe_id):
    recipe = get_object_or_404(
        Favorites, recipe=recipe_id, user=request.user
    )
    if recipe.delete():
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
