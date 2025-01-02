from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from ..models import Project
import json
from openai import OpenAI
import logging
import traceback

logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key is not configured in settings")
        client = None
    else:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

def get_project_context(project):
    """Generate a rich context from project details"""
    context = f"Project: {project.title}\nDescription: {project.description}\n"
    
    if project.related_idea:
        context += f"\nCore Idea: {project.related_idea.description}"
    
    if project.ai_response_json:
        try:
            market_data = json.loads(project.ai_response_json)
            if 'market_overview' in market_data:
                overview = market_data['market_overview']
                context += "\n\nMarket Context:"
                if 'key_players' in overview:
                    context += f"\nKey Competitors: {', '.join(overview['key_players'])}"
                if 'competitive_intensity' in overview:
                    context += f"\nMarket Competition: {overview['competitive_intensity']}"
            if 'market_gaps' in market_data:
                gaps = market_data['market_gaps']
                if 'opportunities' in gaps:
                    context += f"\nMarket Opportunities: {', '.join(gaps['opportunities'])}"
        except:
            pass
    
    return context

@login_required
def project_content_generator(request, project_id):
    """Handle content generation requests"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user has permission to view
        if project.creator != request.user and request.user not in project.team_members.all():
            return JsonResponse({
                'error': "You don't have permission to access this project's content generator."
            }, status=403)
        
        # Handle AJAX request for content generation
        if request.method == "POST":
            # Verify OpenAI client is initialized
            if not client:
                return JsonResponse({
                    'error': 'OpenAI API key is not configured. Please contact support.'
                }, status=500)
            
            try:
                # Parse request body
                data = json.loads(request.body.decode('utf-8'))
                
                # Extract and validate fields
                content_type = data.get('content_type', '')
                topic = data.get('topic', '')
                key_points = data.get('key_points', '')
                tone = data.get('tone', 'professional')
                
                # Validate required fields
                if not all([content_type, topic, key_points]):
                    missing_fields = []
                    if not content_type: missing_fields.append('content_type')
                    if not topic: missing_fields.append('topic')
                    if not key_points: missing_fields.append('key_points')
                    
                    return JsonResponse({
                        'error': f"Missing required fields: {', '.join(missing_fields)}"
                    }, status=400)
                
                # Get project context
                project_context = get_project_context(project)
                
                # Construct system message based on content type and project context
                system_message = f"""You are a specialized content creator for a startup project with the following context:

{project_context}

Your role is to create {content_type} content that specifically addresses this project's unique aspects, market position, and target audience. Focus on:
1. The project's specific value propositions
2. Its market differentiation
3. Addressing identified market gaps
4. Speaking directly to the target audience's needs"""
                
                # Construct user message with specific instructions
                format_instructions = {
                    'email': "Format this as a professional email with a compelling subject line and well-structured body. Include a clear call-to-action.",
                    'blog': "Format this as a blog post with an SEO-optimized title, engaging introduction, well-organized sections with subheadings, and a strong conclusion.",
                    'social': "Format this as an engaging social media post optimized for sharing. Include relevant hashtags and a compelling call-to-action.",
                    'marketing': "Format this as persuasive marketing copy that highlights benefits, addresses pain points, and includes a strong call-to-action."
                }.get(content_type, "")
                
                user_message = f"""Create a {tone} {content_type} about {topic} that aligns with our project's goals and market position.

Key points to include:
{key_points}

{format_instructions}

Requirements:
- Maintain a {tone} tone throughout
- Reference our project's unique value propositions
- Address specific market gaps and opportunities identified
- Focus on our target audience's needs
- Use clear and concise language
- Ensure content is engaging and valuable"""
                
                try:
                    # Call OpenAI API with GPT-4
                    response = client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=0.7,
                        max_tokens=2000,
                        top_p=0.9,
                        frequency_penalty=0.3,
                        presence_penalty=0.3
                    )
                    
                    generated_content = response.choices[0].message.content.strip()
                    return JsonResponse({'content': generated_content})
                    
                except Exception as e:
                    logger.error(f"OpenAI API Error: {str(e)}")
                    logger.error(traceback.format_exc())
                    return JsonResponse({
                        'error': 'An error occurred while generating content.',
                        'details': str(e)
                    }, status=500)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {str(e)}")
                return JsonResponse({
                    'error': 'Invalid request format',
                    'details': str(e)
                }, status=400)
                
            except Exception as e:
                logger.error(f"Unexpected Error: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'details': str(e)
                }, status=500)
        
        # Regular page load
        return render(request, 'founder_assistance/project_content_generator.html', {
            'project': project
        })
        
    except Exception as e:
        logger.error(f"View-level Exception: {str(e)}")
        logger.error(traceback.format_exc())
        if request.method == "POST":
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=500)
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
