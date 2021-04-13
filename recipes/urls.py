from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop_list/', views.shop_list, name='shop_list'),
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
]
