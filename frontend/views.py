import os
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
from dotenv import load_dotenv

from agents.orchestration_agent import OrchestrationAgent
from agents.grocery_list_generation_agent import GroceryListGenerationAgent
from agents.recipe_library_agent import RecipeLibraryAgent
from agents.meal_plan_generation_agent import MealPlanGenerationAgent

# Load environment variables
load_dotenv()

# Paths and Keys
COOKBOOK_PATH = os.path.join(settings.BASE_DIR, "data", "cookbook_data.json")
EXPECTED_API_KEY = os.environ.get("API_KEY")

# Instantiate orchestration layer
orchestrator = OrchestrationAgent()


# === View: Upload Cookbook ===
def upload_cookbook(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('cookbook_file'):
        uploaded_file = request.FILES['cookbook_file']
        try:
            context = orchestrator.handle_upload(uploaded_file)
            request.session['cookbook_uploaded'] = True
            messages.success(request, context.get("message", "Cookbook uploaded successfully."))
        except Exception as e:
            messages.error(request, f"❌ Failed to upload cookbook: {str(e)}")
    return render(request, 'upload.html', context)


# === View: Set Preferences ===
def set_preferences(request):
    context = orchestrator.handle_preferences(request)
    return render(request, 'preferences.html', context)


# === View: List Recipes from Cookbook ===
def recipe_list_view(request):
    if not request.session.get("cookbook_uploaded") or not os.path.exists(COOKBOOK_PATH):
        return render(request, "grocery_list.html", {
            "recipe_names": [],
            "api_key": EXPECTED_API_KEY,
            "message": "No cookbook uploaded yet. Please upload one first."
        })

    try:
        agent = GroceryListGenerationAgent(COOKBOOK_PATH)
        recipe_names = agent.get_all_recipe_names()
    except Exception as e:
        recipe_names = []
        print(f"[❌] Failed to load recipes: {e}")

    return render(request, "grocery_list.html", {
        "recipe_names": recipe_names,
        "api_key": EXPECTED_API_KEY
    })


# === View: Generate Grocery List for Selected Recipe ===
def grocery_list_view(request, recipe_name):
    api_key = request.headers.get("x-api-key")
    if api_key != EXPECTED_API_KEY:
        return HttpResponseForbidden("Invalid API Key")

    if not request.session.get("cookbook_uploaded") or not os.path.exists(COOKBOOK_PATH):
        return JsonResponse({"error": "No cookbook uploaded"}, status=400)

    agent = GroceryListGenerationAgent(COOKBOOK_PATH)
    grocery_list = agent.generate_grocery_list_for_recipe(recipe_name)
    return JsonResponse({
        "recipe": recipe_name,
        "grocery_list": grocery_list
    })


# === View: Recipe Library View ===
def recipe_library(request):
    data_file = os.path.join(settings.BASE_DIR, 'data', 'cookbook_data.json')
    agent = RecipeLibraryAgent(data_file)
    recipes = agent.load_recipes()
    return render(request, 'recipe_library.html', {'recipes': recipes})


# === View: Generate Meal Plan ===
def meal_plan_view(request):
    if not request.session.get("cookbook_uploaded"):
        messages.error(request, "Please upload a cookbook first.")
        return render(request, "upload.html")

    cookbook_path = os.path.join(settings.BASE_DIR, "data", "cookbook_data.json")
    try:
        agent = MealPlanGenerationAgent(cookbook_path)
        raw_meal_plan = agent.generate_weekly_meal_plan()
        day_blocks = [block.strip() for block in raw_meal_plan.split("\n\n") if block.strip()]
        request.session['last_generated_meal_plan'] = raw_meal_plan  # ✅ Save to session
    except Exception as e:
        day_blocks = []
        messages.error(request, f"Failed to generate meal plan: {str(e)}")

    return render(request, "meal_plan.html", {"day_blocks": day_blocks})


# === View: Weekly Grocery List using GenAI agent ===
def weekly_grocery_list_view(request):
    api_key = request.headers.get("x-api-key")
    if api_key != EXPECTED_API_KEY:
        return HttpResponseForbidden("Invalid API Key")

    meal_plan_text = request.session.get("last_generated_meal_plan")
    if not meal_plan_text:
        return JsonResponse({"error": "No meal plan found"}, status=400)

    try:
        agent = GroceryListGenerationAgent()
        grocery_dict = agent.generate_grocery_list(meal_plan_text)
        return JsonResponse({"grocery_list": grocery_dict})
    except Exception as e:
        print(f"[❌] Error generating grocery list: {e}")
        return JsonResponse({"error": "Failed to generate grocery list"}, status=500)
