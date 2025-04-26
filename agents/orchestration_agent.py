import os
import json
from django.conf import settings
from django.contrib import messages

from agents.cookbook_ingestion_agent import CookbookIngestionAgent
from agents.user_profiling_agent import UserProfilingAgent
from agents.recipe_library_agent import RecipeLibraryAgent
from agents.grocery_list_generation_agent import GroceryListGenerationAgent
from agents.meal_plan_generation_agent import MealPlanGenerationAgent
from agents.instruction_delivery_agent import InstructionDeliveryAgent

EXPECTED_API_KEY = os.getenv("API_KEY")

class OrchestrationAgent:
    def __init__(self):
        # Setup paths and agents
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.cookbook_path = os.path.join(self.data_dir, 'cookbook_data.json')
        self.mealplans_path = os.path.join(self.data_dir, 'mealplans.json')

    def handle_upload_view(self, request):
        context = {}
        if request.method == 'POST' and request.FILES.get('cookbook_file'):
            uploaded_file = request.FILES['cookbook_file']
            # Handle the uploaded file
            context = self.handle_upload(uploaded_file)
            request.session['cookbook_uploaded'] = True
            messages.success(request, context.get("message", "Cookbook uploaded successfully."))
        return context

    def handle_upload(self, uploaded_file):
        # Actually parse and save the cookbook
        file_path = os.path.join(self.data_dir, uploaded_file.name)
        with open(file_path, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        agent = CookbookIngestionAgent(file_path)
        recipes = agent.parse_cookbook()

        with open(self.cookbook_path, 'w') as f:
            json.dump(recipes, f, indent=2)

        return {"message": f"✅ Successfully parsed {len(recipes)} recipes."}

    def handle_preferences(self, request):
        prefs_file = os.path.join(self.data_dir, 'user_preferences.json')
        agent = UserProfilingAgent(prefs_file)
        options = [
            "Vegan", "Vegetarian", "No dairy", "No gluten",
            "No red meat", "No chicken", "No fish", "Low carb"
        ]

        context = {"options": options}

        if request.method == 'POST':
            selected = request.POST.getlist('preferences')
            custom_note = request.POST.get('custom_note', '')
            agent.store_preferences(selected, custom_note)
            context['message'] = "✅ Preferences saved!"
            context['selected'] = selected
            context['custom_note'] = custom_note
        else:
            existing = agent.load_preferences()
            context['selected'] = existing.get("preferences", [])
            context['custom_note'] = existing.get("custom_note", "")

        return context

    def handle_recipe_list_view(self, request):
        if not request.session.get("cookbook_uploaded") or not os.path.exists(self.cookbook_path):
            return {"recipe_names": [], "api_key": EXPECTED_API_KEY, "message": "No cookbook uploaded yet."}
        
        agent = RecipeLibraryAgent(self.cookbook_path)
        recipes = agent.load_recipes()
        recipe_names = [recipe["name"] for recipe in recipes]
        return {"recipe_names": recipe_names, "api_key": EXPECTED_API_KEY}

    def handle_grocery_list_generation(self, request, recipe_name):
        try:
            agent = GroceryListGenerationAgent()
            grocery_list = agent.generate_grocery_list_for_recipe(recipe_name)
            return {"recipe": recipe_name, "grocery_list": grocery_list}
        except Exception as e:
            print(f"[❌] Error generating grocery list for {recipe_name}: {e}")
            return {"error": f"Failed to generate grocery list for {recipe_name}"}

    def handle_recipe_library_view(self, request):
        agent = RecipeLibraryAgent(self.cookbook_path)
        try:
            recipes = agent.load_recipes()
        except Exception as e:
            recipes = []
            print(f"[❌] Failed to load recipe library: {e}")
        return {"recipes": recipes}

    def handle_display_meal_plan(self, request):
        meal_plan_text = ""

        if os.path.exists(self.mealplans_path):
            if os.path.getsize(self.mealplans_path) > 0:  # ✅ File is not empty
                with open(self.mealplans_path, 'r') as f:
                    try:
                        meal_plan_text = json.load(f).get('meal_plan', '')
                    except json.JSONDecodeError:
                        meal_plan_text = ""
            else:
                meal_plan_text = ""

        day_blocks = [block.strip() for block in meal_plan_text.split("\n\n") if block.strip()]
        return {"day_blocks": day_blocks}

    def handle_generate_meal_plan(self, request):

        if not request.session.get("cookbook_uploaded"):
            messages.error(request, "Please upload a cookbook first.")
            return {"day_blocks": []}

        try:
            agent = MealPlanGenerationAgent(self.cookbook_path)
            raw_meal_plan = agent.generate_weekly_meal_plan()
            day_blocks = [block.strip() for block in raw_meal_plan.split("\n\n") if block.strip()]

            # Save meal plan
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.mealplans_path, 'w') as f:
                json.dump({"meal_plan": raw_meal_plan}, f, indent=2)

            messages.success(request, "✅ New meal plan generated successfully!")
            return {"day_blocks": day_blocks}
        except Exception as e:
            print(f"[❌] Failed to generate meal plan: {e}")
            messages.error(request, f"Failed to generate meal plan: {str(e)}")
            return {"day_blocks": []}

    def handle_display_weekly_grocery_list(self, request):
        cleaned_list = ""

        grocery_list_path = os.path.join(settings.BASE_DIR, 'data', 'grocery_list.json')
        if os.path.exists(grocery_list_path) and os.path.getsize(grocery_list_path) > 0:
            try:
                with open(grocery_list_path, 'r') as f:
                    grocery_list_data = json.load(f)
                    cleaned_list = grocery_list_data.get('grocery_list', '')
            except json.JSONDecodeError:
                cleaned_list = ""

        return {"cleaned_list": cleaned_list}

    def handle_generate_weekly_grocery_list(self, request):

        try:
            agent = GroceryListGenerationAgent()
            grocery_list = agent.generate_full_weekly_grocery_list()

            # Save in session
            request.session['weekly_grocery_list'] = grocery_list

            return {"grocery_list": grocery_list}
        except Exception as e:
            print(f"[❌] Error generating weekly grocery list: {e}")
            return {"grocery_list": {}, "message": "Failed to generate grocery list"}
        
    def handle_instruction_delivery_page(self, request):

        agent = InstructionDeliveryAgent()
        weekly_instructions = agent.load_weekly_instructions()

        if not request.session.get("cookbook_uploaded") or not os.path.exists(self.cookbook_path):
            messages.error(request, "Please upload a cookbook first.")
            return {"weekly_instructions": weekly_instructions}

        return {
            "api_key": os.getenv("API_KEY"),
            "weekly_instructions": weekly_instructions
        }

    def handle_generate_weekly_instructions(self, request):

        if not request.session.get("cookbook_uploaded") or not os.path.exists(self.cookbook_path):
            return {"error": "No cookbook uploaded"}

        meal_plan_text = request.session.get("last_generated_meal_plan")
        if not meal_plan_text:
            return {"error": "No meal plan found"}

        try:
            agent = InstructionDeliveryAgent()
            weekly_instructions = agent.generate_weekly_instructions(meal_plan_text)
            return {"weekly_instructions": weekly_instructions}
        except Exception as e:
            print(f"[❌] Error generating weekly instructions: {e}")
            return {"error": "Failed to generate instructions"}