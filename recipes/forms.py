from django import forms

from .models import Ingredient, Recipe, Tag


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
    image = forms.ImageField(
        required=True, error_messages={'required': 'Не выбрано фото'}
    )
    duration = forms.fields.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form__input', 'value': 10,
                   'autocomplete': 'off'}
        )
    )

    def clean(self):
        super(RecipeForm, self).clean()
        ingredients = []
        clean_ingredients = []
        amounts = []
        tags_list = []
        for i, j in self.data.items():
            if j == 'on':
                tags_list.append(i)
        if not tags_list:
            self._errors['tag'] = self.error_class(
                ['Не выбран ни один тэг']
            )

        for _ in self.data:
            ingredients = self.data.getlist('nameIngredient')
            if not ingredients:
                self._errors['ingredient'] = self.error_class(
                    ['Не выбран ни один ингредиент']
                )
            amounts = self.data.getlist('valueIngredient')

        for ingredient in ingredients:
            clear_ingredient = Ingredient.objects.filter(title=ingredient)
            if clear_ingredient:
                if ingredient in clean_ingredients:
                    self._errors['ingredient'] = self.error_class(
                        [f'Элемент \'{ingredient}\' уже был выбран']
                    )
                clean_ingredients.append(ingredient)
            else:
                self._errors['ingredient'] = self.error_class(
                    [f'Элемента \'{ingredient}\' нет в БД'])

        for amount in amounts:
            if int(amount) <= 0:
                self._errors['ingredient'] = self.error_class(
                    ['Должно быть положительное число']
                )
        return self.cleaned_data
