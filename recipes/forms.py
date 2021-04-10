from django import forms
from django.forms import ModelForm

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):

    error_messages = {
        'tag': 'не добавлены теги',
        'ingredients': 'не добавлены ингридиенты'
    }

    class Meta:
        model = Recipe
        fields = (
            'title',
            'description',
            'image',
            'duration',
        )
