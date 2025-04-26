import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
from dotenv import load_dotenv

from agents.orchestration_agent import OrchestrationAgent

# Load environment variables
load_dotenv()

# Keys and Settings
EXPECTED_API_KEY = os.getenv("API_KEY")
DEBUG = getattr(settings, "DEBUG", True)

# Instantiate Orchestration Agent
orchestrator = OrchestrationAgent()

# === View: Upload Cookbook ===
def upload_cookbook(request):
    context = orchestrator.handle_upload_view(request)
    return render(request, 'upload.html', context)

# === View: Set Preferences ===
def set_preferences(request):
    context = orchestrator.handle_preferences(request)
    return render(request, 'preferences.html', context)

# === View: List Recipes for Selection ===
def recipe_list_view(request):
    context = orchestrator.handle_recipe_list_view(request)
    return render(request, "grocery_list.html", context)

# === View: Recipe Library View ===
def recipe_library(request):
    context = orchestrator.handle_recipe_library_view(request)
    return render(request, 'recipe_library.html', context)

# === View: Meal Plan Generation View ===
def meal_plan_view(request):
    if request.method == 'POST':
        context = orchestrator.handle_generate_meal_plan(request)
    else:
        context = orchestrator.handle_display_meal_plan(request)

    return render(request, "meal_plan.html", context)

# === View: Weekly Grocery List from Meal Plan ===
def weekly_grocery_list_view(request):
    if request.method == "POST":
        context = orchestrator.handle_generate_weekly_grocery_list(request)
    else:
        context = orchestrator.handle_display_weekly_grocery_list(request)

    return render(request, "grocery_list.html", context)