import csv
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

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
    paginator = Paginator(recipe, 6)
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
    if request.method == 'GET':
        tags = Tag.objects.all()
        form = RecipeForm()
        context = {'form': form, 'tags': tags}
        return render(request, 'new_recipe.html', context)
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES)
        tags = get_tag(request)
        ingedient_names = request.POST.getlist('nameIngredient')
        ingredient_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        if not tags:
            form.add_error('tag', 'Обязательное поле')
        if not ingedient_names:
            form.add_error('ingredient', 'Ингредиент не выбран')
        if not form.is_valid():
            tags = Tag.objects.all()
            context = {'form': form, 'tags': tags}
            return render(request, 'new_recipe.html', context)
        tags = get_tag(request)
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        products = [Ingredient.objects.get(
            title=ingedient_names[i],
            dimension=ingredient_units[i]
        ) for i in range(len(ingedient_names))]
        ingredients = []
        for i in range(len(amounts)):
            ingredients.append(IngredientItem(
                recipe=recipe, ingredients=products[i], count=amounts[i]))
        IngredientItem.objects.bulk_create(ingredients)
        for i in tags:
            tag = get_object_or_404(Tag, title=i)
            recipe.tag.add(tag)
        form.save_m2m()
        return redirect('index')


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)


@login_required(login_url='accounts/login/')
@login_required()
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
            return render(request, 'forbiten.html')
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        tags = get_tag(request)
        ingedient_names = request.POST.getlist('nameIngredient')
        ingredient_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        if not tags:
            form.add_error('tag', 'Обязательное поле')
        if not ingedient_names:
            form.add_error('ingredient', 'Ингредиент не выбран')
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'edit_recipe.html', context)
        form.save()
        products_num = len(ingedient_names)
        new_ingredients = []
        IngredientItem.objects.filter(recipe__id=recipe_id).delete()
        for i in range(products_num):
            product = Ingredient.objects.get(title=ingedient_names[i],
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
@login_required()
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    author = recipe.author
    if user == author:
        recipe.delete()
    return render(request, 'forbiten.html')


@login_required
def get_ingredients(request):
    text = request.GET.get('query').rstrip('/')
    data = []
    ingredients = Ingredient.objects.filter(
        title__startswith=text).all()
    for ingredient in ingredients:
        data.append(
            {'title': ingredient.title, 'dimension': ingredient.dimension})
    return JsonResponse(data, safe=False)


@login_required
def purchases_list(request):
    user = request.user
    my_shop_list = ShopList.objects.filter(user=user.id).first()
    if my_shop_list:
        recipes = my_shop_list.recipes.all()
    else:
        recipes = None
    return render(
        request,
        template_name='shopList.html', context={'recipes': recipes})


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
        shop_list = ShopList.objects.get_or_create(user=user.id)[0]
        current_recipe = get_object_or_404(Recipe, id=recipe_id)
        shop_list.recipes.remove(current_recipe)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def purchases_delete_index(request, recipe_id):
    user = request.user
    shop_list = ShopList.objects.get_or_create(user=user.id)[0]
    current_recipe = get_object_or_404(Recipe, id=recipe_id)
    shop_list.recipes.remove(current_recipe)
    return redirect('purchases_list')


@login_required
def purchases_download(request):
    shops = get_object_or_404(ShopList, user=request.user)
    recipes = shops.recipes.all()
    ingredients = IngredientItem.objects.filter(
        recipe__in=recipes).select_related('ingredients').values(
        'ingredients__title', 'ingredients__dimension').annotate(
        count=Sum('count')).all()
    header = 'Список покупок\n\n'
    response = HttpResponse(header, content_type='text/txt')
    response['Content-Disposition'] = 'attachment; filename="purchases.txt"'

    writer = csv.writer(response)

    for ingredient in ingredients:
        name = ingredient['ingredients__title']
        dimension = ingredient['ingredients__dimension']
        count = ingredient['count']
        writer.writerow([f'{name} ({dimension}) - {count}'])

    return response


@login_required
def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipe = Recipe.objects.select_related('author').filter(
        author=author).order_by('-pub_date').all()
    tags_values = request.GET.getlist('filters')
    if tags_values:
        recipe = recipe.filter(tag__title__in=tags_values).distinct().all()
    tags = Tag.objects.all()
    paginator = Paginator(recipe, 6)
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


@login_required
def follow(request):
    authors_list = Subscribe.objects.select_related('user', 'author').filter(
        user=request.user
    )
    paginator = Paginator(authors_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
    return render(request, 'myFollow.html', context)


@login_required(login_url='accounts/login/')
@require_POST
def subscription(request):
    json_data = json.loads(request.body.decode())
    author = get_object_or_404(User, id=json_data['id'])
    is_exist = Subscribe.objects.filter(
        user=request.user, author=author).exists()
    data = {'success': 'true'}
    if is_exist:
        data['success'] = 'false'
    else:
        Subscribe.objects.create(user=request.user, author=author)
    return JsonResponse(data)


@login_required(login_url='accounts/login/')
@require_http_methods('DELETE')
def delete_subscription(request, author_id):
    author = get_object_or_404(User, id=author_id)
    data = {'success': 'true'}
    follow = Subscribe.objects.filter(
        user=request.user, author=author)
    if not follow:
        data['success'] = 'false'
    follow.delete()
    return JsonResponse(data)


@login_required(login_url='accounts/login/')
@login_required
def favorite_index(request, ):
    tags_values = request.GET.getlist('filters')
    recipe_list = Recipe.objects.filter(
        fans__user_id=request.user.id).all()
    if tags_values:
        recipe_list = recipe_list.filter(
            tag__title__in=tags_values
        ).distinct()
    tags = Tag.objects.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator, 'tags': tags}
    return render(request, 'favorite.html', context)


@login_required(login_url='accounts/login/')
@login_required
def favorites_add(request):
    recipe_id = json.loads(request.body)['id']
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if Favorites.objects.get_or_create(user=request.user, recipe=recipe):
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required(login_url='accounts/login/')
@login_required
def favorites_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    author = get_object_or_404(User, username=request.user.username)
    favorites = get_object_or_404(Favorites, user=author, recipe=recipe)
    if favorites.delete():
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
