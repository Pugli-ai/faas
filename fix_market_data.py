import os
import django
import json
from tempfile import NamedTemporaryFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ideapools.settings')
django.setup()

# Import after Django setup
from founder_assistance.models import Project

# Create market analysis data
market_data = {
    "market_size_and_growth": {
        "current_size": "1000000",
        "growth_projections": "15",
        "key_drivers": ["Technology Adoption", "Market Expansion"]
    },
    "market_segments": {
        "segments": ["Enterprise", "SMB"],
        "growth_potential": {
            "Enterprise": "20",
            "SMB": "25"
        }
    },
    "market_trends": {
        "current_trends": ["Digital Transformation", "Cloud Migration"],
        "emerging_opportunities": ["AI Integration", "Remote Work Solutions"]
    },
    "market_challenges": {
        "entry_barriers": ["High Initial Investment", "Market Competition"],
        "regulatory_challenges": ["Data Privacy Laws", "Industry Standards"],
        "risks": ["Technology Changes", "Economic Uncertainty"]
    }
}

# Write to temp file to ensure proper JSON formatting
with NamedTemporaryFile(mode='w+', delete=False) as f:
    json.dump(market_data, f, indent=2)
    temp_path = f.name

# Read back the properly formatted JSON
with open(temp_path, 'r') as f:
    validated_data = json.load(f)

# Update the project
project = Project.objects.get(id=16)
project.ai_response_json = validated_data
project.save()

# Verify the update
updated_project = Project.objects.get(id=16)
print("Updated project data:")
print(json.dumps(updated_project.ai_response_json, indent=2))

# Cleanup
os.unlink(temp_path)
