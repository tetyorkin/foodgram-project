from django import template
from django.utils.html import strip_tags

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
