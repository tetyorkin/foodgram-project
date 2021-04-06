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


@login_required
def new_recipe(request):
    tags = Tag.objects.all()
    form = RecipeForm()
    if request.method == "POST":
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingredients_req = get_ingredients_from_js(request)
        if not ingredients_req:
            form.add_error(None, 'Добавьте ингредиенты')
        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            for title, count in ingredients_req.items():
                ingredient = get_object_or_404(Ingredient, title=title)
                recipe_ingredient = IngredientItem(
                    count=count, ingredients=ingredient, recipe=recipe
                )
                recipe_ingredient.save()
            form.save_m2m()
            return redirect('index')
    context = {'form': form, 'tags': tags}
    return render(request, 'new_recipe.html', context)


@login_required
def recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {'recipe': recipe}
    return render(request, 'recipe.html', context)


@login_required(login_url='auth/login/')
@require_http_methods(['GET', 'POST'])
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
        recipe_tags = recipe.tags.all()
        context = {
            'form': form,
            'recipe': recipe,
            'ingredients': ingredients,
            'recipe_tags': recipe_tags
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
