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
from .utils import get_ingredients_from_js, get_form_ingredients


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
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        print(form.is_valid())
        print(form.errors)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'recipe.html', context)
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
        tags = ['breakfast', 'lunch', 'dinner']
        for tag in tags:
            if request.POST.get(tag) is not None:
                current_tag = get_object_or_404(Tag, name=tag)
                form.tag.add(current_tag)
        return redirect('index')


@login_required
def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)


@login_required(login_url='auth/login/')
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    # GET-запрос на страницу редактирования рецепта
    if request.method == 'GET':
        form = RecipeForm(
            request.POST or None,
            files=request.FILES or None,
            instance=recipe
        )
        ingredients = recipe.ingredients.all()
        tags = recipe.tag.all()

        context = {
            'form': form,
            'recipe': recipe,
            'ingredients': ingredients,
            'tags': tags
        }
        return render(request, 'edit_recipe.html', context)
    # POST-запрос с данными из формы редактирования рецепта
    elif request.method == 'POST':
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'edit_recipe.html', context)
        form.save()
        print(request.POST)
        new_titles = request.POST.getlist('nameIngredient')
        new_units = request.POST.getlist('unitsIngredient')
        amounts = request.POST.getlist('valueIngredient')
        products_num = len(new_titles)
        new_ingredients = []
        IngredientItem.objects.filter(recipe__id=recipe_id).delete()
        for i in range(products_num):
            product = Ingredient.objects.get(title=new_titles[i], dimension=new_units[i])
            new_ingredients.append(IngredientItem(recipe=recipe, ingredients=product, count=amounts[i]))
        IngredientItem.objects.bulk_create(new_ingredients)
        return redirect('index')


@login_required(login_url='auth/login/')
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
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
