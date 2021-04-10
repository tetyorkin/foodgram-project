from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from users.models import User
from .models import Recipe, Tag, IngredientItem, Ingredient, ShopList
from .forms import RecipeForm
from .utils import get_ingredients_from_js, get_form_ingredients, \
    get_tag_create_recipe


def index(request):
    recipe_list = Recipe.objects.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
        # 'tag_filters': tag_filters
    }
    # if request.user.is_authenticated:
        # favorites = Recipe.objects.filter(favorite_recipe__user=request.user)
        # wishlist = Recipe.objects.filter(wishlist_recipe__user=request.user)
        # context['wishlist'] = wishlist
        # context['favorites'] = favorites
    return render(request, 'index.html', context)


@login_required(login_url='auth/login/')
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


@login_required
def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)


@login_required(login_url='auth/login/')
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
            product = Ingredient.objects.get(title=new_titles[i], dimension=new_units[i])
            new_ingredients.append(IngredientItem(recipe=recipe, ingredients=product, count=amounts[i]))
        IngredientItem.objects.bulk_create(new_ingredients)
        tags = get_tag_create_recipe(request)
        recipe.tag.clear()
        if not tags:
            form.add_error(None, 'Не добавлены теги')
        for i in tags:
            tag = get_object_or_404(Tag, title=i)
            recipe.tag.add(tag)
        return redirect('index')


@login_required()
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    print(recipe)
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
    raw = JsonResponse(data, safe=False)
    return JsonResponse(data, safe=False)


@login_required
def shop_list(request):
    user = request.user
    my_shop_list = ShopList.objects.filter(user=user.id).first()
    if my_shop_list:
        recipes = my_shop_list.recipes.all()
    else:
        recipes = None
    return render(
        request,
        template_name='shopList.html', context={'recipes': recipes})


# @login_required
# def profile(request, user_id):
#     profile = get_object_or_404(User, id=user_id)
#     tags = request.GET.getlist('tag')
#     recipes_list = Recipe.recipes.tag_filter(tags)
#     paginator = Paginator(recipes_list.filter(author=profile), 6)
#     page_number = request.GET.get('page')
#     page = paginator.get_page(page_number)
#     context = {
#         'all_tags': Tag.objects.all(),
#         'profile': profile,
#         'page': page,
#         'paginator': paginator
#     }
#     # Если юзер авторизован, добавляет в контекст список
#     # покупок и избранное
#     user = request.user
#     if user.is_authenticated:
#         _add_subscription_status(context, user, profile)
#         _extend_context(context, user)
#     return render(request, 'authorRecipe.html', context)
