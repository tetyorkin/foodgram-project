from django import forms
from django.forms import ModelForm

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = (
            'title',
            'tag',
            'duration',
            'description',
            'image',
        )
        widgets = {
            'tag': forms.CheckboxSelectMultiple(),
        }
