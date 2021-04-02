from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_recipe/', views.new_recipe, name='new_recipe'),
    path('recipes/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('edit_recipe/<int:pk>/', views.recipe_edit, name='recipe_edit'),
]
