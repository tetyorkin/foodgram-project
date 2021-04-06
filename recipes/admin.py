from django.contrib import admin

from .models import Ingredient, Recipe, Subscribe, Tag, IngredientItem


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


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Subscribe)
