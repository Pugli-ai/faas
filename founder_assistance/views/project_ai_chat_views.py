from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages  # Renamed to avoid confusion
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

def get_or_create_legal_assistant():
    """Create or get the legal assistant"""
    try:
        # List all assistants to find existing legal assistant
        assistants = client.beta.assistants.list()
        legal_assistant = next((a for a in assistants.data if a.name == "Legal Advisor"), None)
        
        if legal_assistant:
            return legal_assistant.id
            
        # Create new assistant if none exists
        assistant = client.beta.assistants.create(
            name="Legal Advisor",
            instructions="""You are a legal consultant specializing in startup law within the European Union (EU). 
            Provide expert guidance on the following key areas, focusing on early-stage companies operating or 
            planning to operate in EU jurisdictions:

            1. Company Formation & Structure
            2. Regulatory Compliance
            3. Intellectual Property Protection
            4. Employment Law
            5. Data Protection & GDPR
            6. Contract Law
            7. Investment & Funding Regulations
            8. Tax Compliance
            9. Cross-border Operations
            10. E-commerce Regulations

            Provide clear, actionable advice while emphasizing when formal legal counsel should be sought.""",
            model="gpt-4-1106-preview"
        )
        print(f"[INFO] Created new legal assistant with ID: {assistant.id}")
        return assistant.id
    except Exception as e:
        print(f"[ERROR] Failed to create/get legal assistant: {str(e)}")
        logger.error(f"Failed to create/get legal assistant: {str(e)}")
        return None

@login_required
@require_http_methods(["GET", "POST"])
def project_legal_chat(request, project_id):
    """Handle legal assistant chat interactions"""
    print(f"\n[DEBUG] Legal Chat View - Method: {request.method}")
    print(f"[DEBUG] Project ID: {project_id}")
    
    try:
        print("[DEBUG] Starting view execution")
        project = get_object_or_404(Project, id=project_id)
        chat_messages = []  # Initialize empty messages list
        thread_id = request.GET.get('thread_id')  # Move thread_id initialization here
        print(f"[DEBUG] Project found, thread_id: {thread_id}")
        
        # Check if user has permission
        if project.creator != request.user and request.user not in project.team_members.all():
            if request.method == "POST":
                return JsonResponse({
                    'error': "You don't have permission to access this project's legal assistant."
                }, status=403)
            django_messages.error(request, "You don't have permission to access this project's legal assistant.")
            return redirect('founder_assistance:project_detail', project_id=project_id)
        
        print("[DEBUG] User permission check passed")
        
        # Handle chat message
        if request.method == "POST":
            print("[DEBUG] Processing POST request")
            
            # Verify OpenAI client is initialized and API key is set
            if not client or not settings.OPENAI_API_KEY:
                print("[ERROR] OpenAI client is not configured or API key is missing")
                return JsonResponse({
                    'error': 'OpenAI API is not configured properly. Please check your environment variables.'
                }, status=500)
            
            try:
                # Get or create legal assistant
                assistant_id = get_or_create_legal_assistant()
                if not assistant_id:
                    return JsonResponse({
                        'error': 'Failed to initialize legal assistant'
                    }, status=500)
                
                # Parse request body
                data = json.loads(request.body)
                user_message = data.get('message', '').strip()
                thread_id = data.get('thread_id')
                
                print(f"[DEBUG] Message: {user_message}")
                print(f"[DEBUG] Thread ID: {thread_id}")
                
                if not user_message:
                    return JsonResponse({
                        'error': 'Message cannot be empty'
                    }, status=400)
                
                # Create new thread if none exists
                if not thread_id:
                    thread = client.beta.threads.create()
                    thread_id = thread.id
                    print(f"[DEBUG] Created new thread: {thread_id}")
                
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
                print(f"[ERROR] JSON Decode Error: {str(e)}")
                return JsonResponse({
                    'error': 'Invalid request format'
                }, status=400)
                
            except Exception as e:
                print(f"[ERROR] Chat Error: {str(e)}")
                logger.error(f"Chat Error: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'error': 'An error occurred while processing your message'
                }, status=500)
        
        print("[DEBUG] Processing GET request")
        # For GET request, try to load existing thread messages if thread_id is provided
        if thread_id and client:
            try:
                print(f"[DEBUG] Loading messages for thread: {thread_id}")
                thread_messages = client.beta.threads.messages.list(thread_id=thread_id)
                chat_messages = [
                    {
                        'role': msg.role,
                        'content': msg.content[0].text.value if msg.content else ''
                    }
                    for msg in thread_messages
                ]
                print(f"[DEBUG] Loaded {len(chat_messages)} messages")
            except Exception as e:
                print(f"[ERROR] Failed to load thread messages: {str(e)}")
                logger.error(f"Failed to load thread messages: {str(e)}")
                logger.error(traceback.format_exc())
                # Don't raise error, just continue with empty messages list
        
        print("[DEBUG] Rendering template")
        # Regular page load
        context = {
            'project': project,
            'chat_messages': chat_messages,
            'thread_id': thread_id
        }
        print(f"[DEBUG] Context: {context}")
        return render(request, 'founder_assistance/project_legal_chat.html', context)
        
    except Exception as e:
        print(f"[ERROR] View-level Exception: {str(e)}")
        logger.error(f"View-level Exception: {str(e)}")
        logger.error(traceback.format_exc())
        if request.method == "POST":
            return JsonResponse({
                'error': 'An unexpected error occurred'
            }, status=500)
        django_messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
