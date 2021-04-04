from django.contrib import admin

from recipes.models import (Ingredient, IngredientItem, Recipe, ShopList, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'pub_date', 'duration',)
    search_fields = ('title', 'description')
    list_filter = ('pub_date',)


# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'title', 'style', 'slug')
#     search_fields = ('title',)
#     list_filter = ('title',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension',)
    search_fields = ('title',)
    list_filter = ('title', 'dimension')


@admin.register(IngredientItem)
class IngredientItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredients', 'count')

#
#
# @admin.register(ShopList)
# class ShopListAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'user',)
#     search_fields = ('user',)
#     list_filter = ('user',)



from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    IngredientItem,
    Subscribe,
    ShopList,
    Tag,
)


# class RecipeIngreInline(admin.TabularInline):
#     model = IngredientItem
#     extra = 1
#
#
# class RecipeAdmin(admin.ModelAdmin):
#     inlines = (RecipeIngreInline,)
#
#
# class IngredientAdmin(admin.ModelAdmin):
#     inlines = (RecipeIngreInline,)
#




# admin.site.register(Ingredient, IngredientAdmin)
# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(IngredientItem)
# admin.site.register(Subscribe)
# admin.site.register(ShopList)
