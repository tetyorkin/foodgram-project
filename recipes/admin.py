from django.contrib import admin

from .models import Ingredient, IngredientItem, Recipe, Subscribe, Tag, \
    Favorites, ShopList


class IngredientInline(admin.TabularInline):
    model = IngredientItem
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
    list_display = ('pk', 'title', 'author', 'pub_date', 'description',
                    'image', 'duration')
    search_fields = ('title',)
    list_filter = ('title',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension')
    search_fields = ('title',)
    list_filter = ('title',)


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'color',
        'name',
    )
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created')


class ShoplistAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created')


admin.site.register(Tag, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Subscribe)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShopList, ShoplistAdmin)
