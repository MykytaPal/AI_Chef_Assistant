import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class GroceryListGenerationAgent:
    def __init__(self, cookbook_path: str):
        self.cookbook_path = cookbook_path
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def load_recipes(self) -> List[dict]:
        if not os.path.exists(self.cookbook_path):
            raise FileNotFoundError(f"No cookbook found at {self.cookbook_path}")
        with open(self.cookbook_path, 'r') as f:
            return json.load(f)

    def get_all_recipe_names(self) -> List[str]:
        recipes = self.load_recipes()
        return [recipe["name"] for recipe in recipes]

    def get_ingredients_for_recipe(self, recipe_name: str) -> Optional[List[str]]:
        recipes = self.load_recipes()
        for recipe in recipes:
            if recipe_name.lower() in recipe["name"].lower():
                print(f"[🔎] Matched recipe: {recipe['name']}")
                return recipe.get("ingredients", [])
        print(f"[⚠️] No match found for '{recipe_name}'. Try again.")
        return None

    def ask_llm_to_clean_ingredients(self, raw_ingredients: List[str]) -> List[str]:
        prompt = f"""
You are an ingredient normalization assistant.

Given a list of raw ingredient lines, return a JSON array of the core grocery items needed.
Do not include quantities or units. Remove duplicates. Focus on the **main grocery item** only.

Ingredients:
{json.dumps(raw_ingredients, indent=2)}

Return a JSON list like:
["eggs", "milk", "flour"]
        """

        try:
            response = self.llm.invoke(prompt)
            return json.loads(response.content.strip())
        except Exception as e:
            print(f"[❌] LLM failed to extract grocery list: {e}")
            return []

    def generate_grocery_list_for_recipe(self, recipe_name: str) -> List[str]:
        raw_ingredients = self.get_ingredients_for_recipe(recipe_name)
        if not raw_ingredients:
            return []
        cleaned = self.ask_llm_to_clean_ingredients(raw_ingredients)
        cleaned_sorted = sorted(set(cleaned))
        print(f"[✅] Grocery list for '{recipe_name}': {cleaned_sorted}")
        return cleaned_sorted

    def save_grocery_list(self, recipe_name: str, output_path: str = "data/grocery_list.json"):
        grocery_list = self.generate_grocery_list_for_recipe(recipe_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(grocery_list, f, indent=2)
        print(f"[💾] Grocery list for '{recipe_name}' saved to {output_path}")


# ✅ CLI Entry point for testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agents/grocery_list_generation_agent.py <path_to_cookbook.json>")
        sys.exit(1)

    cookbook_path = sys.argv[1]
    agent = GroceryListGenerationAgent(cookbook_path)

    print("\n📚 Available Recipes:")
    for name in agent.get_all_recipe_names():
        print(f" - {name}")

    recipe = input("\nEnter a recipe name to get the grocery list: ")
    grocery_list = agent.generate_grocery_list_for_recipe(recipe)

    if grocery_list:
        print(f"\n🛒 Grocery List for '{recipe}':")
        for item in grocery_list:
            print(f" - {item}")
        agent.save_grocery_list(recipe)
