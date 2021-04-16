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

    widgets = {
        'title': forms.TextInput(
            attrs={'class': 'form__input', 'autocomplete': 'off'}
        ),
        'description': forms.Textarea(
            attrs={'class': 'form__textarea', 'rows': 8}
        ),
        'image': forms.FileInput(
            attrs={'style': 'font-family: "Montserrat", sans-serif;'}
        ),
    }

    tag = forms.ModelMultipleChoiceField(
        Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    ingredient = forms.CharField(max_length=250, required=False)
    image = forms.ImageField(required=True)
    duration = forms.fields.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form__input', 'value': 10,
                   'autocomplete': 'off'}
        )
    )
