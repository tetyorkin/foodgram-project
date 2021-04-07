from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_recipe/', views.new_recipe, name='new_recipe'),
    path('recipes/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('recipes/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('edit_recipe/<int:recipe_id>/', views.recipe_edit, name='recipe_edit'),
    path('ingredients/', views.get_ingredients, name="get_ingredients"),
    path('shop_list/', views.shop_list, name='shop_list'),
]
