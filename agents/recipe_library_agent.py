import os
import json

class RecipeLibraryAgent:
    def __init__(self, data_path):
        self.data_path = data_path

    def load_recipes(self):
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []