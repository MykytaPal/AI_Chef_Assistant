from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_cookbook, name='upload_cookbook'),
    path('preferences/', views.set_preferences, name='set_preferences'),
]