from django.contrib import admin

from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'dimension')
    search_fields = ('title',)
    list_filter = ('id',)


admin.site.register(Ingredient, IngredientAdmin)
