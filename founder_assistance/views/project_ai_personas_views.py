"""
AI-powered user personas generation.
This module handles user personas creation using AI.
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from ..models import Project
from openai import OpenAI
import logging
import traceback

logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    if not settings.OPENAI_API_KEY:
        print("[WARNING] OpenAI API key is not set in settings")
        logger.warning("OpenAI API key is not configured in settings")
        client = None
    else:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        print("[INFO] OpenAI client configured successfully with API key from settings")
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI client: {str(e)}")
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

def generate_user_personas(project):
    """
    Generate user personas using OpenAI based on project details.
    """
    try:
        if not client:
            return None, "OpenAI client is not configured properly"

        # Prepare context from project details
        context = {
            "title": project.title,
            "description": project.description or "",
            "idea_description": project.related_idea.description if project.related_idea else "",
        }
        
        # Construct the prompt for OpenAI
        prompt = f"""
        Based on the following project details, generate 3 detailed user personas in a specific JSON format.
        
        Project Title: {context['title']}
        Project Description: {context['description']}
        Related Idea: {context['idea_description']}
        
        Requirements for each persona:
        1. name_age: String with name and age (e.g., "Sarah Chen, 28")
        2. background: String describing occupation, education, and lifestyle
        3. goals_motivations: String listing their primary goals and what drives them
        4. pain_points: String describing their main frustrations and challenges
        5. tech_comfort: String indicating level as either "High", "Medium", or "Low" with brief explanation
        6. preferred_channels: String listing their preferred ways of discovering and using products
        7. quote: String with a characteristic statement from this persona
        8. personality_traits: String with comma-separated traits (exactly 4 traits)

        The response must be a JSON array with exactly 3 persona objects. Each object must have all the fields above.
        Example format:
        [
            {{
                "name_age": "Sarah Chen, 28",
                "background": "Marketing manager at a tech startup, MBA graduate, urban lifestyle enthusiast",
                "goals_motivations": "Seeking efficient solutions to streamline work processes and achieve better work-life balance",
                "pain_points": "Struggles with managing multiple projects and maintaining team communication",
                "tech_comfort": "High - Early adopter of new technologies and comfortable with digital tools",
                "preferred_channels": "LinkedIn, Professional blogs, Industry conferences, Mobile apps",
                "quote": "I need tools that can keep up with my fast-paced work environment",
                "personality_traits": "Ambitious, Analytical, Tech-savvy, Results-driven"
            }},
            ...
        ]

        Ensure each persona is distinct and relevant to the project's context. Always format personality_traits as exactly 4 comma-separated traits.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a UX research expert specializing in user personas. You must always respond with valid JSON in the exact format specified, with no deviations or additional fields."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        # Parse the response and return personas
        personas_text = response.choices[0].message.content.strip()
        
        # Ensure we're working with clean JSON by removing any markdown formatting
        if personas_text.startswith("```json"):
            personas_text = personas_text[7:-3]
        elif personas_text.startswith("```"):
            personas_text = personas_text[3:-3]
            
        personas = json.loads(personas_text)
        
        # Validate the response format
        if not isinstance(personas, list) or len(personas) != 3:
            raise ValueError("Response must contain exactly 3 personas")
        
        required_fields = ['name_age', 'background', 'goals_motivations', 'pain_points', 
                         'tech_comfort', 'preferred_channels', 'quote', 'personality_traits']
        
        for persona in personas:
            # Check all required fields are present
            if not all(field in persona for field in required_fields):
                raise ValueError("Each persona must have all required fields")
            
            # Validate personality traits format
            traits = persona['personality_traits'].split(',')
            if len(traits) != 4:
                raise ValueError("Each persona must have exactly 4 personality traits")
        
        return personas, None
        
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing AI response: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return None, error_msg
    except Exception as e:
        error_msg = f"Error generating personas: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return None, error_msg

@login_required
def project_user_personas(request, project_id):
    """
    View for generating and displaying user personas for a project.
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if request.user != project.creator and request.user not in project.team_members.all():
        messages.error(request, "You don't have permission to access this project.")
        return redirect('founder_assistance:project_list')
    
    try:
        # Get existing personas if available
        personas = None
        if project.personas_data:
            try:
                personas = json.loads(project.personas_data)
            except json.JSONDecodeError:
                logger.error("Failed to parse existing personas data")
                project.personas_data = None
                project.save()
        
        if request.method == 'POST':
            # Verify OpenAI client is initialized
            if not client:
                messages.error(request, "OpenAI API is not configured properly. Please check your environment variables.")
                return render(request, 'founder_assistance/project_user_personas.html', {
                    'project': project,
                    'personas': personas
                })

            # Generate personas using OpenAI
            new_personas, error = generate_user_personas(project)
            
            if new_personas:
                # Store the personas in the project's personas_data field
                project.personas_data = json.dumps(new_personas)
                project.save()
                messages.success(request, "User personas generated successfully!")
                personas = new_personas
            else:
                messages.error(request, f"Failed to generate user personas: {error}")
        
        return render(request, 'founder_assistance/project_user_personas.html', {
            'project': project,
            'personas': personas
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in user personas view: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, "An unexpected error occurred. Please try again.")
        return render(request, 'founder_assistance/project_user_personas.html', {
            'project': project,
            'personas': None
        })
