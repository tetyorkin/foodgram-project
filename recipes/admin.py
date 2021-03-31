from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    IngredientItem,
    Subscribe,
    ShopList,
    Tag,
)


class RecipeIngreInline(admin.TabularInline):
    model = IngredientItem
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngreInline,)


class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngreInline,)





admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientItem)
admin.site.register(Subscribe)
admin.site.register(ShopList)
