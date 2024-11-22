"""
AI-powered customer research views.
This module handles customer segmentation analysis using AI.
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
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
        # Explicitly pass the API key from Django settings
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        print("[INFO] OpenAI client configured successfully with API key from settings")
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI client: {str(e)}")
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

def generate_customer_segments(project):
    """
    Generate customer segments using OpenAI based on project details.
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
        Based on the following project details, generate 3 distinct customer segments:
        
        Project Title: {context['title']}
        Project Description: {context['description']}
        Related Idea: {context['idea_description']}
        
        For each segment, provide:
        1. Demographics (age, income, location, etc.)
        2. Pain Points (problems they face)
        3. Needs (what they're looking for)
        4. Buying Behavior (how they make purchase decisions)
        5. Marketing Approach (how to reach and convince them)
        
        Format the response as a JSON array with 3 objects, each containing the fields: demographics, pain_points, needs, buying_behavior, and marketing_approach.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a customer research expert specializing in market segmentation. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        # Parse the response and return segments
        segments_text = response.choices[0].message.content.strip()
        
        # Ensure we're working with clean JSON by removing any markdown formatting
        if segments_text.startswith("```json"):
            segments_text = segments_text[7:-3]  # Remove ```json and ``` markers
        elif segments_text.startswith("```"):
            segments_text = segments_text[3:-3]  # Remove ``` markers
            
        segments = json.loads(segments_text)
        return segments, None
        
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing AI response: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return None, error_msg
    except Exception as e:
        error_msg = f"Error generating segments: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return None, error_msg

def process_segment_data(segments):
    """
    Process segment data to convert lists into properly formatted strings.
    """
    processed_segments = []
    for segment in segments:
        processed_segment = {}
        for key, value in segment.items():
            if isinstance(value, list):
                # Join list items with proper formatting
                processed_segment[key] = '\n• ' + '\n• '.join(value)
            elif isinstance(value, dict):
                # Format dictionary values into readable text
                formatted_items = []
                for k, v in value.items():
                    formatted_items.append(f"{k}: {v}")
                processed_segment[key] = '\n• ' + '\n• '.join(formatted_items)
            else:
                processed_segment[key] = value
        processed_segments.append(processed_segment)
    return processed_segments

@login_required
def project_customer_research(request, project_id):
    """
    View for generating and displaying customer segments for a project.
    """
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user has access to this project
        if request.user != project.creator and request.user not in project.team_members.all():
            messages.error(request, "You don't have permission to access this project.")
            return redirect('founder_assistance:project_list')
        
        if request.method == 'POST':
            # Verify OpenAI client is initialized
            if not client:
                messages.error(request, "OpenAI API is not configured properly. Please check your environment variables.")
                return redirect('founder_assistance:project_customer_research', project_id=project_id)

            # Generate segments using OpenAI
            segments, error = generate_customer_segments(project)
            
            if segments:
                # Store the segments in the project's AI response fields
                project.ai_response_raw = json.dumps(segments)
                project.ai_response_json = segments
                project.save()
                
                messages.success(request, "Customer segments generated successfully!")
            else:
                messages.error(request, f"Failed to generate customer segments: {error}")
        
        # Get existing segments if available and process them
        segments = project.ai_response_json if project.ai_response_json else None
        if segments:
            segments = process_segment_data(segments)
        
        return render(request, 'founder_assistance/project_customer_research.html', {
            'project': project,
            'segments': segments
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in customer research view: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
