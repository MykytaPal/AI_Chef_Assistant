import os
import json
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

class GroceryListGenerationAgent:
    def __init__(self):
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.mealplans_path = os.path.join(self.data_dir, 'mealplans.json')
        self.cookbook_path = os.path.join(self.data_dir, 'cookbook_data.json')
        self.grocery_list_path = os.path.join(self.data_dir, 'grocery_list.json')
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def generate_full_weekly_grocery_list(self):
        if not os.path.exists(self.mealplans_path) or not os.path.exists(self.cookbook_path):
            return {}

        # Load meal plan
        with open(self.mealplans_path, 'r') as f:
            meal_plan_data = json.load(f)
        meal_plan_text = meal_plan_data.get('meal_plan', '')

        # Load cookbook recipes
        with open(self.cookbook_path, 'r') as f:
            recipes = json.load(f)

        # Build a raw ingredient list
        raw_ingredients = []

        recipe_name_to_ingredients = {
            recipe.get('name', '').lower(): recipe.get('ingredients', []) for recipe in recipes
        }

        for line in meal_plan_text.splitlines():
            for recipe_name, ingredients in recipe_name_to_ingredients.items():
                if recipe_name in line.lower():
                    raw_ingredients.extend(ingredients)

        if not raw_ingredients:
            return {}

        # Build smart prompt
        prompt = (
            "You are a helpful assistant tasked with preparing a grocery list for a week's worth of meals.\n"
            "Combine the following ingredients into a clean grocery list.\n"
            "Group duplicate ingredients together, sum the quantities where possible, and present it in a bulleted list.\n"
            "If quantities are missing or inconsistent, make your best guess.\n"
            "Format the list neatly without headers:\n\n"
        )

        for ingredient in raw_ingredients:
            prompt += f"- {ingredient}\n"

        # Query LLM
        response = self.llm.invoke([
            HumanMessage(content=prompt)
        ])

        cleaned_list_text = response.content

        # === SAVE the cleaned list ===
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.grocery_list_path, 'w') as f:
            json.dump({"grocery_list": cleaned_list_text}, f, indent=2)

        return {"cleaned_list": cleaned_list_text}