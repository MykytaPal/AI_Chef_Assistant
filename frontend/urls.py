from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_cookbook, name='upload_cookbook'),
    path('preferences/', views.set_preferences, name='set_preferences'),

    # Show all recipes
    path('grocery-list/', views.recipe_list_view, name='recipe_list'),

    # Dynamic grocery list fetch by recipe name
    path('grocery-list/<str:recipe_name>/', views.grocery_list_view, name='grocery_list'),
]


