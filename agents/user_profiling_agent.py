import os
import json

class UserProfilingAgent:
    def __init__(self, profile_path):
        self.profile_path = profile_path
        if not os.path.exists(self.profile_path):
            with open(self.profile_path, 'w') as f:
                json.dump({}, f)

    def store_preferences(self, preferences, custom_note=""):
        print("[🧠] Saving user preferences...")
        data = {
            "preferences": preferences,
            "custom_note": custom_note
        }
        with open(self.profile_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("[✅] Preferences stored.")

    def load_preferences(self):
        if not os.path.exists(self.profile_path):
            return {}
        try:
            with open(self.profile_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    print("[⚠️] Preferences file is empty.")
                    return {}
                return json.loads(content)
        except Exception as e:
            print(f"[❌] Failed to load preferences: {e}")
            return {}

    def match_preferences_to_recipe(self, recipe):
        """
        Optional filtering function. Returns True if recipe matches preferences.
        """
        user_prefs = self.load_preferences()
        prefs = user_prefs.get("preferences", [])
        if not prefs:
            return True  # No filter

        text = f"{recipe['name']} {recipe['ingredients']} {recipe['instructions']}".lower()
        blocked = [p for p in prefs if p.lower().replace("no ", "") in text]
        return len(blocked) == 0