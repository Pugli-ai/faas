from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
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
    """Generate project-specific context for legal advice"""
    context = f"""Project Details:
- Name: {project.title}
- Description: {project.description}"""
    
    if project.related_idea:
        context += f"\n- Core Idea: {project.related_idea.description}"
    
    if project.ai_response_json:
        try:
            market_data = json.loads(project.ai_response_json)
            if 'market_overview' in market_data:
                overview = market_data['market_overview']
                if 'market_share' in overview:
                    context += f"\n- Market Position: {overview['market_share']}"
            if 'competitor_strategies' in market_data:
                strategies = market_data['competitor_strategies']
                if 'business_models' in strategies:
                    context += f"\n- Business Models: {', '.join(strategies['business_models'])}"
        except:
            pass
    
    return context

def get_or_create_legal_assistant(project):
    """Create or get the legal assistant with project context"""
    try:
        project_context = get_project_context(project)
        
        # List all assistants to find existing project-specific assistant
        assistants = client.beta.assistants.list()
        assistant_name = f"Legal Advisor - {project.title}"
        legal_assistant = next((a for a in assistants.data if a.name == assistant_name), None)
        
        if legal_assistant:
            # Update existing assistant with latest project context
            legal_assistant = client.beta.assistants.update(
                legal_assistant.id,
                instructions=f"""You are a legal consultant specializing in startup law within the European Union (EU), 
                specifically advising on the following project:

                {project_context}

                Provide expert guidance tailored to this specific project's needs, focusing on:

                1. Company Formation & Structure
                   - Recommend appropriate legal structures based on the project's specific needs
                   - Address jurisdiction-specific requirements

                2. Regulatory Compliance
                   - Identify specific regulations that apply to this project
                   - Provide compliance guidance for the project's business model

                3. Intellectual Property Protection
                   - Advise on protecting the project's specific innovations
                   - Guide on trademark and patent considerations

                4. Data Protection & GDPR
                   - Provide specific GDPR compliance guidance based on the project's data handling
                   - Address privacy requirements for the target market

                5. Contract & Commercial Law
                   - Guide on contracts needed for this specific business model
                   - Address terms of service and user agreements

                6. Investment & Funding
                   - Advise on legal aspects of funding for this specific project
                   - Guide on investor agreements and terms

                Always provide clear, actionable advice while emphasizing when formal legal counsel should be sought.
                Focus on practical steps that align with the project's current stage and goals."""
            )
            return legal_assistant.id
            
        # Create new assistant if none exists
        assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions=f"""You are a legal consultant specializing in startup law within the European Union (EU), 
            specifically advising on the following project:

            {project_context}

            Provide expert guidance tailored to this specific project's needs, focusing on:

            1. Company Formation & Structure
               - Recommend appropriate legal structures based on the project's specific needs
               - Address jurisdiction-specific requirements

            2. Regulatory Compliance
               - Identify specific regulations that apply to this project
               - Provide compliance guidance for the project's business model

            3. Intellectual Property Protection
               - Advise on protecting the project's specific innovations
               - Guide on trademark and patent considerations

            4. Data Protection & GDPR
               - Provide specific GDPR compliance guidance based on the project's data handling
               - Address privacy requirements for the target market

            5. Contract & Commercial Law
               - Guide on contracts needed for this specific business model
               - Address terms of service and user agreements

            6. Investment & Funding
               - Advise on legal aspects of funding for this specific project
               - Guide on investor agreements and terms

            Always provide clear, actionable advice while emphasizing when formal legal counsel should be sought.
            Focus on practical steps that align with the project's current stage and goals.""",
            model="gpt-4-1106-preview"
        )
        logger.info(f"Created new legal assistant for project {project.title}")
        return assistant.id
    except Exception as e:
        logger.error(f"Failed to create/get legal assistant: {str(e)}")
        return None

@login_required
@require_http_methods(["GET", "POST"])
def project_legal_chat(request, project_id):
    """Handle legal assistant chat interactions"""
    try:
        project = get_object_or_404(Project, id=project_id)
        chat_messages = []
        thread_id = request.GET.get('thread_id')
        
        # Check if user has permission
        if project.creator != request.user and request.user not in project.team_members.all():
            if request.method == "POST":
                return JsonResponse({
                    'error': "You don't have permission to access this project's legal assistant."
                }, status=403)
            django_messages.error(request, "You don't have permission to access this project's legal assistant.")
            return redirect('founder_assistance:project_detail', project_id=project_id)
        
        # Handle chat message
        if request.method == "POST":
            # Verify OpenAI client is initialized
            if not client:
                return JsonResponse({
                    'error': 'OpenAI API is not configured properly. Please contact support.'
                }, status=500)
            
            try:
                # Get or create project-specific legal assistant
                assistant_id = get_or_create_legal_assistant(project)
                if not assistant_id:
                    return JsonResponse({
                        'error': 'Failed to initialize legal assistant'
                    }, status=500)
                
                # Parse request body
                data = json.loads(request.body)
                user_message = data.get('message', '').strip()
                thread_id = data.get('thread_id')
                
                if not user_message:
                    return JsonResponse({
                        'error': 'Message cannot be empty'
                    }, status=400)
                
                # Create new thread if none exists
                if not thread_id:
                    thread = client.beta.threads.create()
                    thread_id = thread.id
                
                # Add message to thread
                client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=user_message
                )
                
                # Create and run the assistant
                run = client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistant_id
                )
                
                # Wait for completion
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    if run_status.status == 'completed':
                        break
                    elif run_status.status in ['failed', 'cancelled', 'expired']:
                        return JsonResponse({
                            'error': f'Assistant run {run_status.status}'
                        }, status=500)
                
                # Get the assistant's response
                thread_messages = client.beta.threads.messages.list(thread_id=thread_id)
                assistant_message = next(msg for msg in thread_messages if msg.role == "assistant")
                response_content = assistant_message.content[0].text.value
                
                return JsonResponse({
                    'thread_id': thread_id,
                    'response': response_content
                })
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {str(e)}")
                return JsonResponse({
                    'error': 'Invalid request format'
                }, status=400)
                
            except Exception as e:
                logger.error(f"Chat Error: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'error': 'An error occurred while processing your message'
                }, status=500)
        
        # For GET request, try to load existing thread messages
        if thread_id and client:
            try:
                thread_messages = client.beta.threads.messages.list(thread_id=thread_id)
                chat_messages = [
                    {
                        'role': msg.role,
                        'content': msg.content[0].text.value if msg.content else ''
                    }
                    for msg in thread_messages
                ]
            except Exception as e:
                logger.error(f"Failed to load thread messages: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Regular page load
        return render(request, 'founder_assistance/project_legal_chat.html', {
            'project': project,
            'chat_messages': chat_messages,
            'thread_id': thread_id
        })
        
    except Exception as e:
        logger.error(f"View-level Exception: {str(e)}")
        logger.error(traceback.format_exc())
        if request.method == "POST":
            return JsonResponse({
                'error': 'An unexpected error occurred'
            }, status=500)
        django_messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
