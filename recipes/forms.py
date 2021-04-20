from django import forms

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = (
            'title',
            'description',
            'image',
            'duration',
        )


    tag = forms.ModelMultipleChoiceField(
        Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    ingredient = forms.CharField(max_length=250, required=False)
    description = forms.CharField(widget=forms.Textarea)
    duration = forms.fields.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form__input', 'value': 10,
                   'autocomplete': 'off'}
        )
    )
