from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_recipe/', views.new_recipe, name='new_recipe'),
    path('profile/<username>/', views.profile, name='profile'),
    path('recipe/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('ingredients/', views.get_ingredients, name='get_ingredients'),
    path('edit_recipe/<int:recipe_id>/', views.recipe_edit, name='recipe_edit'),
    path('follow/', views.follow, name='follow'),
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('subscriptions/', views.subscription, name='subscription'),
    path('subscriptions/<int:author_id>', views.delete_subscription,
         name='delete_subscription'),
    path('favorite/', views.favorite_index, name='favorite_index'),
    path('favorites/add/', views.favorites_add, name='favorite_add'),
    path('favorites/<int:recipe_id>/', views.favorites_delete,
         name='favorite_delete'),
    path('purchases_list/', views.purchases_list, name='purchases_list'),
    path('purchases_list/download', views.purchases_download, name='purchases_download'),
    path('purchases/add/', views.purchases_add, name='purchases_add'),
    path('purchases/<int:recipe_id>/delete/', views.purchases_delete_index, name='purchases_delete_index'),
    path('purchases/<int:recipe_id>/', views.purchases_delete,
         name='purchases_delete'),
]
