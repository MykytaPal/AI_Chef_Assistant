import os
import json
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

class InstructionDeliveryAgent:
    def __init__(self):
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.mealplans_path = os.path.join(self.data_dir, 'mealplans.json')
        self.instructions_path = os.path.join(self.data_dir, 'instructions.json')
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def generate_weekly_instructions(self, meal_plan_text):
        if not meal_plan_text:
            return []

        prompt = (
            "You are a helpful cooking assistant. Based on the following meal plan, generate simple and clear cooking instructions for each meal (breakfast, lunch, dinner) for each day.\n\n"
            "Meal Plan:\n"
            f"{meal_plan_text}\n\n"
            "Format the output as JSON, like this:\n"
            "[\n"
            "  {\"day\": \"Monday\", \"breakfast\": \"...\", \"lunch\": \"...\", \"dinner\": \"...\"},\n"
            "  {\"day\": \"Tuesday\", \"breakfast\": \"...\", \"lunch\": \"...\", \"dinner\": \"...\"},\n"
            "  ...\n"
            "]"
        )

        response = self.llm.invoke([
            HumanMessage(content=prompt)
        ])

        try:
            weekly_instructions = json.loads(response.content)
        except json.JSONDecodeError:
            weekly_instructions = []

        # Save instructions to file
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.instructions_path, 'w') as f:
            json.dump({"weekly_instructions": weekly_instructions}, f, indent=2)

        return weekly_instructions

    def load_weekly_instructions(self):
        if os.path.exists(self.instructions_path) and os.path.getsize(self.instructions_path) > 0:
            try:
                with open(self.instructions_path, 'r') as f:
                    data = json.load(f)
                    return data.get("weekly_instructions", [])
            except json.JSONDecodeError:
                return []
        return []