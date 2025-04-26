import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load API Key
load_dotenv()

class InstructionDeliveryAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.2,
            model_name="gpt-3.5-turbo",
        )

    def generate_weekly_instructions(self, meal_plan_text):
        prompt = f"""
You are a smart AI meal assistant.

Given this weekly meal plan, generate clear, simple, **day-by-day** cooking instructions.

For **each day**, provide:
- Breakfast instructions
- Lunch instructions
- Dinner instructions

Return a **JSON array** like this:
[
  {{
    "day": "Monday",
    "breakfast": "Instructions for breakfast...",
    "lunch": "Instructions for lunch...",
    "dinner": "Instructions for dinner..."
  }},
  ...
]

ONLY return valid parsable JSON. Do NOT add any explanations.

Meal Plan:
{meal_plan_text}
"""

        try:
            response = self.llm.invoke(prompt)
            if not response or not response.content.strip():
                raise ValueError("Empty response from LLM")
            
            weekly_instructions = json.loads(response.content.strip())
            return weekly_instructions

        except Exception as e:
            print(f"[❌] Failed to generate instructions: {e}")
            return []
