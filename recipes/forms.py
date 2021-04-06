from django import forms
from django.forms import ModelForm

from .models import Recipe


class RecipeForm(ModelForm):

    class Meta:
        model = Recipe
        fields = (
            'title',
            # 'tags',
            # 'ingredient',
            'duration',
            'description',
            'image'
        )
        widgets = {
            'tag': forms.CheckboxSelectMultiple(),
        }

