from django import template
from django.utils.html import strip_tags
from recipes.models import Subscribe, ShopList

register = template.Library()


@register.filter(name='add_classes')
def add_classes(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='remove_tag')
def remove_tag(value):
    new_value = value.replace('<li>', '').replace('</li>', '\n')
    return strip_tags(new_value)


@register.filter(name='remove_email')
def remove_email(value):
    new_value = strip_tags(value)
    return new_value.replace('email', '')


@register.filter(name="get_filter_values")
def get_filter_values(title):
    return title.getlist("filters")


@register.filter(name='get_filter_link')
def get_filter_link(request, tag):
    new_request = request.GET.copy()
    if tag.title in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag.title)
        new_request.setlist('filters', filters)
    else:
        new_request.appendlist('filters', tag.title)

    return new_request.urlencode()


@register.filter(name='is_follower')
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
def pluralize(value, endings):
    # print(value)
    print(endings)
    endings = endings.split(',')
    if value % 100 in (11, 12, 13, 14):
        return endings[2]
    if value % 10 == 1:
        return endings[0]
    if value % 10 in (2, 3, 4):
        return endings[1]
    else:
        return endings[2]
