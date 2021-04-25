from django import forms
from django.contrib import admin
from django.forms import BaseInlineFormSet

from .models import (Favorites, Ingredient, IngredientItem, Recipe, ShopList,
                     Subscribe, Tag)


class IngredienInlineFormSet(BaseInlineFormSet):

    def _construct_form(self, i, **kwargs):
        form = super(IngredienInlineFormSet, self)._construct_form(i, **kwargs)
        if i < 1:
            form.empty_permitted = False
        return form


class IngredientInline(admin.TabularInline):
    formset = IngredienInlineFormSet
    model = IngredientItem
    extra = 1
    fields = ('ingredients', 'count', )


class RecipeForm(forms.ModelForm):

    def clean(self):
        super(RecipeForm, self).clean()
        if 'image' in self.data.keys():
            self._errors['image'] = self.error_class(
                ['Не выбрано фото']
            )
        return self.cleaned_data


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeForm
    inlines = (IngredientInline,)
    list_display = ('pk', 'title', 'author', 'pub_date', 'description',
                    'image', 'duration')
    search_fields = ('title', 'author__username')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension')
    search_fields = ('title',)


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'color',
        'name',
    )
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class SubscribeForm(forms.ModelForm):

    def clean(self):
        super(SubscribeForm, self).clean()
        author = self.data.get('author')
        user = self.data.get('user')
        if author == user:
            self._errors['author'] = self.error_class(
                ['Пользователь не может подписаться а себя']
            )
        return self.cleaned_data


class SubscribeAdmin(admin.ModelAdmin):
    form = SubscribeForm
    list_display = ('user', 'author',)
    search_fields = ('user__username', 'author__username',)


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__title',)


class ShoplistAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


admin.site.register(Tag, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShopList, ShoplistAdmin)
