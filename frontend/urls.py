from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_cookbook, name='upload_cookbook'),
    path('preferences/', views.set_preferences, name='set_preferences'),
    path('meal-plan/', views.meal_plan_view, name='meal_plan'),
    path('grocery-list/', views.recipe_list_view, name='recipe_list'),
    path('weekly-grocery-list/', views.weekly_grocery_list_view, name='weekly_grocery_list'),
    path('grocery-list/<str:recipe_name>/', views.grocery_list_view, name='grocery_list_api'),  # ⬅️ / at end!
    path('recipe-library/', views.recipe_library, name='recipe_library'),
]