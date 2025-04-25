import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class MealPlanGenerationAgent:
    def __init__(self, cookbook_json_path):
        self.cookbook_path = cookbook_json_path
        self.recipes = self.load_recipes()
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-4",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def load_recipes(self):
        if not os.path.exists(self.cookbook_path):
            raise FileNotFoundError(f"Cookbook file not found at: {self.cookbook_path}")
        with open(self.cookbook_path, "r") as file:
            return json.load(file)

    def generate_prompt(self):
        recipe_names = [r['name'] for r in self.recipes]
        recipe_list = "\n".join([f"- {name}" for name in recipe_names])

        return f"""
        You are a meal planning assistant.

        Here is a list of recipes:
        {recipe_list}

        Using these recipes, create a weekly meal plan (Monday to Sunday) with:
        - Breakfast
        - Lunch
        - Dinner

        Guidelines:
        - Do not repeat any recipe more than twice.
        - Ensure variety across meals.
        - Include the recipe name only (no ingredients or instructions).

        Format:
        Monday:
        - Breakfast: ...
        - Lunch: ...
        - Dinner: ...
        (continue through Sunday)
        """

    def generate_weekly_meal_plan(self):
        prompt = self.generate_prompt()

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"[❌] Failed to generate meal plan: {e}")
            return None
