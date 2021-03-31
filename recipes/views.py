from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse

from .models import Recipe, Tag, IngredientItem, Ingredient
from .forms import RecipeForm
from .utils import get_ingredients_from_js


def index(request):
    recipe_list = Recipe.objects.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get("page")
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
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
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
    else:
        form = RecipeForm()
    return render(
        request,
        'formRecipe.html',
        {
            'form': form,
            'tags': tags,
        },
    )
