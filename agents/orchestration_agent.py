import os
from agents.user_profiling_agent import UserProfilingAgent
from agents.cookbook_ingestion_agent import CookbookIngestionAgent
from django.conf import settings
import json

class OrchestrationAgent:
    def __init__(self):
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        self.prefs_path = os.path.join(self.data_dir, 'user_preferences.json')
        self.cookbook_path = os.path.join(self.data_dir, 'cookbook_data.json')

    def handle_upload(self, uploaded_file):
        file_path = os.path.join(self.data_dir, uploaded_file.name)
        with open(file_path, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        agent = CookbookIngestionAgent(file_path)
        recipes = agent.parse_cookbook()

        with open(self.cookbook_path, 'w') as f:
            json.dump(recipes, f, indent=2)

        return {
            "message": f"✅ Successfully parsed {len(recipes)} recipes from {uploaded_file.name}."
        }

    def handle_preferences(self, request):
        profiling_agent = UserProfilingAgent(self.prefs_path)

        options = [
            "Vegan", "Vegetarian", "No dairy", "No gluten",
            "No red meat", "No chicken", "No fish", "Low carb"
        ]

        context = {"options": options}

        if request.method == 'POST':
            selected = request.POST.getlist('preferences')
            custom_note = request.POST.get('custom_note', '')
            profiling_agent.store_preferences(selected, custom_note)

            context['message'] = "✅ Preferences saved!"
            context['selected'] = selected
            context['custom_note'] = custom_note
        else:
            existing = profiling_agent.load_preferences()
            context['selected'] = existing.get("preferences", [])
            context['custom_note'] = existing.get("custom_note", "")

        return context