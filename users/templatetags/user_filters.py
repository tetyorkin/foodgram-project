from django import template
from django.utils.html import strip_tags

from recipes.models import Favorites, ShopList, Subscribe

register = template.Library()


@register.filter()
def add_classes(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter()
def remove_li(value):
    new_value = value.replace('<li>', '').replace('</li>', '\n')
    return strip_tags(new_value)


@register.filter()
def url_with_get(request, number):
    query = request.GET.copy()
    query['page'] = number
    return query.urlencode()


@register.filter()
def get_filter_values(title):
    return title.getlist('filters')


@register.filter()
def get_filter_link(request, tag):
    new_request = request.GET.copy()
    if tag.title in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag.title)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.title)
    return new_request.urlencode()


@register.filter()
def is_follower(request, profile):
    if Subscribe.objects.filter(
        user=request.user, author=profile
    ).exists():
        return True
    return False


@register.filter
def count_recipes(request):
    my_shop_list = ShopList.objects.get_or_create(user=request.user)[0]
    recipes_amount = my_shop_list.recipes.count()
    return recipes_amount


@register.filter
def even(num):
    if (num % 10 == 1) and (num % 100 != 11):
        word_out = 'рецепт'
    elif (num % 10 >= 2) and (num % 10 <= 4) and (
            num % 100 < 10 or num % 100 >= 20):
        word_out = 'рецепта'
    else:
        word_out = 'рецептов'
    return word_out


@register.filter
def is_favorite(request, recipe_id):
    is_exists = Favorites.objects.filter(
        user=request.user,
        recipe=recipe_id
    ).exists()
    return is_exists


@register.filter
def in_shop_list(request, recipe_id):
    is_exists = ShopList.objects.filter(
        user=request.user, recipes=recipe_id
    ).exists()
    return is_exists
