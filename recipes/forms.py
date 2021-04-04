from django import forms
from django.forms import ModelForm

from .models import Recipe


class RecipeForm(ModelForm):

    class Meta:
        model = Recipe
        fields = (
            'title',
            'tags',
            'ingredients',
            'duration',
            'description',
            'image')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8, 'class': 'form__textarea'}),
        }
