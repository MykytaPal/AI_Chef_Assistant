import os
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
from agents.orchestration_agent import OrchestrationAgent
from agents.grocery_list_generation_agent import GroceryListGenerationAgent
from agents.recipe_library_agent import RecipeLibraryAgent

COOKBOOK_PATH = "data/cookbook_data.json"
EXPECTED_API_KEY = os.environ.get("API_KEY")

orchestrator = OrchestrationAgent()

def upload_cookbook(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('cookbook_file'):
        uploaded_file = request.FILES['cookbook_file']
        context = orchestrator.handle_upload(uploaded_file)
        request.session['cookbook_uploaded'] = True  # ✅ Session flag
        messages.success(request, "Cookbook uploaded successfully.")
    return render(request, 'upload.html', context)

def set_preferences(request):
    context = orchestrator.handle_preferences(request)
    return render(request, 'preferences.html', context)

def recipe_list_view(request):
    # ✅ Only allow if session says so AND file exists
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
    
def recipe_library(request):
    data_file = os.path.join(settings.BASE_DIR, 'data', 'cookbook_data.json')
    agent = RecipeLibraryAgent(data_file)
    recipes = agent.load_recipes()
    return render(request, 'recipe_library.html', {'recipes': recipes})
