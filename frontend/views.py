import os
import json
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from agents.cookbook_ingestion_agent import CookbookIngestionAgent

def upload_cookbook(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('cookbook_file'):
        uploaded_file = request.FILES['cookbook_file']
        file_path = os.path.join(settings.BASE_DIR, 'data', uploaded_file.name)

        # Save file
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Parse with CookbookIngestionAgent
        try:
            agent = CookbookIngestionAgent(file_path)
            recipes = agent.parse_cookbook()

            # Save to cookbook_data.json
            output_path = os.path.join(settings.BASE_DIR, 'data', 'cookbook_data.json')
            with open(output_path, 'w') as f:
                json.dump(recipes, f, indent=2)

            context['message'] = f"✅ Successfully parsed {len(recipes)} recipes from {uploaded_file.name}."
        except Exception as e:
            context['message'] = f"❌ Failed to parse cookbook: {str(e)}"

    return render(request, 'upload.html', context)