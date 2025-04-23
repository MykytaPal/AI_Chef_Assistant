from django.shortcuts import render
from agents.orchestration_agent import OrchestrationAgent

orchestrator = OrchestrationAgent()

def upload_cookbook(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('cookbook_file'):
        uploaded_file = request.FILES['cookbook_file']
        context = orchestrator.handle_upload(uploaded_file)
    return render(request, 'upload.html', context)


def set_preferences(request):
    context = orchestrator.handle_preferences(request)
    return render(request, 'preferences.html', context)