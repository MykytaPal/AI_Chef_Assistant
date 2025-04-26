import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

class GroceryListGenerationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.2,
            model="gpt-4",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_prompt(self, structured_meal_plan: list) -> str:
        return f"""
You are a grocery planning assistant.

Given a structured weekly meal plan with days, recipes, ingredients, and instructions, generate a final grocery list.

Rules:
- For each grocery item, combine the quantities across recipes.
- Use appropriate units like pieces, grams, cups, tablespoons, etc.
- If units differ, pick the most common or most reasonable one.
- Summarize duplicated items correctly (e.g., 2 eggs + 4 eggs = 6 eggs).
- Only include ingredients, no instructions or recipe names in the final list.
- Return only a valid JSON object where the key is the grocery item and the value is the total quantity.

Meal Plan Data:
{json.dumps(structured_meal_plan, indent=2)}

Output Format Example:
{{
  "eggs": "6 pieces",
  "milk": "1 cup",
  "avocado": "2",
  "bread": "4 slices",
  "chicken breast": "400g",
  ...
}}
        """

    def generate_weekly_grocery_list(self, structured_meal_plan: list):
        prompt = self.generate_prompt(structured_meal_plan)
        try:
            response = self.llm.invoke(prompt)
            grocery_list = json.loads(response.content.strip())
            print("[✅] Weekly grocery list generated successfully.")
            return grocery_list
        except Exception as e:
            print(f"[❌] Failed to generate grocery list: {e}")
            return {}

# === CLI Usage for Testing ===
if __name__ == "__main__":
    sample_meal_plan = [
        {
            "day": "Monday",
            "recipes": [
                {
                    "name": "Omelette",
                    "ingredients": ["2 eggs", "1 tbsp milk", "salt"],
                    "instructions": "Whisk eggs and cook with milk."
                },
                {
                    "name": "Avocado Toast",
                    "ingredients": ["1 avocado", "2 slices bread", "salt"],
                    "instructions": "Mash avocado and spread on toast."
                }
            ]
        },
        {
            "day": "Tuesday",
            "recipes": [
                {
                    "name": "Chicken Salad",
                    "ingredients": ["200g chicken breast", "1 cup lettuce", "1 tomato"],
                    "instructions": "Grill chicken and toss with veggies."
                }
            ]
        }
    ]

    agent = GroceryListGenerationAgent()
    grocery_list = agent.generate_weekly_grocery_list(sample_meal_plan)

    print("\n🛒 Final Grocery List for the Week:")
    for item, qty in grocery_list.items():
        print(f" - {item}: {qty}")
