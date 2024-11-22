from founder_assistance.models import Project
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ideapools.settings')
django.setup()

data = {
    "market_size_and_growth": {
        "current_size": "0",
        "growth_projections": "0",
        "key_drivers": []
    },
    "market_segments": {
        "segments": [],
        "growth_potential": {}
    },
    "market_trends": {
        "current_trends": [],
        "emerging_opportunities": []
    },
    "market_challenges": {
        "entry_barriers": [],
        "regulatory_challenges": [],
        "risks": []
    }
}

project = Project.objects.get(id=16)
project.ai_response_json = data
project.save()

print("Updated project data:", json.dumps(Project.objects.get(id=16).ai_response_json, indent=2))
