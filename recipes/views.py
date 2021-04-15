import csv
import json
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from users.models import User
from .models import Recipe, Tag, IngredientItem, Ingredient, ShopList, \
    Subscribe, Favorites
from .forms import RecipeForm
from .utils import get_ingredients_from_js, get_form_ingredients, \
    get_tag_create_recipe, render_to_pdf


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
    # if request.user.is_authenticated:
    # favorites = Recipe.objects.filter(favorite_recipe__user=request.user)
    # wishlist = Recipe.objects.filter(wishlist_recipe__user=request.user)
    # context['wishlist'] = wishlist
    # context['favorites'] = favorites
    return render(request, 'index.html', context)


@login_required(login_url='accounts/login/')
def new_recipe(request):
    if request.method == 'GET':
        tags = Tag.objects.all()
        form = RecipeForm()
        context = {'form': form, 'tags': tags}
        return render(request, 'new_recipe.html', context)
    elif request.method == 'POST':
        print(request.POST)
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'recipe.html', context)
        tags = get_tag_create_recipe(request)
        if not tags:
            form.add_error(None, 'Не добавлены теги')
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        print(request.POST)

        ingedient_names = request.POST.getlist('nameIngredient')
        ingredient_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
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
    elif request.method == 'POST':
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'edit_recipe.html', context)
        form.save()
        print(request.POST)
        new_titles = request.POST.getlist('nameIngredient')
        print(new_titles)
        new_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        products_num = len(new_titles)
        new_ingredients = []
        IngredientItem.objects.filter(recipe__id=recipe_id).delete()
        for i in range(products_num):
            print(new_titles[i])
            product = Ingredient.objects.get(title=new_titles[i],
                                             dimension=new_units[i])
            new_ingredients.append(
                IngredientItem(recipe=recipe, ingredients=product,
                               count=amounts[i]))
        IngredientItem.objects.bulk_create(new_ingredients)
        tags = get_tag_create_recipe(request)
        recipe.tag.clear()
        if not tags:
            form.add_error(None, 'Не добавлены теги')
        for i in tags:
            tag = get_object_or_404(Tag, title=i)
            recipe.tag.add(tag)
        return redirect('index')


@login_required(login_url='auth/login/')
@login_required()
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    author = recipe.author
    if user == author:
        recipe.delete()
    return redirect('index')


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
        my_shop_list = ShopList.objects.get_or_create(user=request.user)[0]
        my_shop_list.recipes.add(recipe)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def purchases_delete(request, recipe_id):
    user = request.user
    my_shop_list = ShopList.objects.get_or_create(user=user.id)[0]
    current_recipe = get_object_or_404(Recipe, id=recipe_id)
    my_shop_list.recipes.remove(current_recipe)
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

    context = {
        'page': page,
        'paginator': paginator,
        'tags': tags,
        'author': author,
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
    context = {"page": page, "paginator": paginator}
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
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'paginator': paginator}
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
