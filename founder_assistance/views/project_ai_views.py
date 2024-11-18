from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from ..models import Project
from ..utils import generate_market_analysis, generate_competitor_analysis
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
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("[INFO] OpenAI client configured successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI client: {str(e)}")
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

@login_required
def project_content_generator(request, project_id):
    """Handle content generation requests"""
    print(f"\n[DEBUG] Content Generator View - Method: {request.method}")
    print(f"[DEBUG] Project ID: {project_id}")
    
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user has permission to view
        if project.creator != request.user and request.user not in project.team_members.all():
            print("[ERROR] Permission denied for user")
            return JsonResponse({
                'error': "You don't have permission to access this project's content generator."
            }, status=403)
        
        # Handle AJAX request for content generation
        if request.method == "POST":
            print("[DEBUG] Processing POST request")
            
            # Verify OpenAI client is initialized
            if not client:
                print("[ERROR] OpenAI client is not configured")
                return JsonResponse({
                    'error': 'OpenAI API key is not configured. Please check your environment variables.'
                }, status=500)
            
            try:
                # Parse request body
                body = request.body.decode('utf-8')
                print(f"[DEBUG] Raw request body: {body}")
                data = json.loads(body)
                
                # Extract and validate fields
                content_type = data.get('content_type', '')
                topic = data.get('topic', '')
                key_points = data.get('key_points', '')
                tone = data.get('tone', 'professional')
                
                print(f"[DEBUG] Parsed data:")
                print(f"- Content Type: {content_type}")
                print(f"- Topic: {topic}")
                print(f"- Tone: {tone}")
                print(f"- Key Points: {key_points}")
                
                # Validate required fields
                if not all([content_type, topic, key_points]):
                    missing_fields = []
                    if not content_type: missing_fields.append('content_type')
                    if not topic: missing_fields.append('topic')
                    if not key_points: missing_fields.append('key_points')
                    
                    print(f"[ERROR] Missing required fields: {', '.join(missing_fields)}")
                    return JsonResponse({
                        'error': f"Missing required fields: {', '.join(missing_fields)}"
                    }, status=400)
                
                # Construct system message based on content type
                system_message = {
                    'email': "You are an expert email copywriter who creates compelling business emails.",
                    'blog': "You are a professional blog writer who creates engaging and SEO-optimized content.",
                    'social': "You are a social media expert who creates viral and engaging posts.",
                    'marketing': "You are a marketing copywriter who creates persuasive content that drives conversions."
                }.get(content_type, "You are a professional content creator skilled in writing compelling business content.")
                
                # Construct user message with specific instructions
                format_instructions = {
                    'email': "Format this as a professional email with a compelling subject line and well-structured body. Include a clear call-to-action.",
                    'blog': "Format this as a blog post with an SEO-optimized title, engaging introduction, well-organized sections with subheadings, and a strong conclusion.",
                    'social': "Format this as an engaging social media post optimized for sharing. Include relevant hashtags and a compelling call-to-action.",
                    'marketing': "Format this as persuasive marketing copy that highlights benefits, addresses pain points, and includes a strong call-to-action."
                }.get(content_type, "")
                
                user_message = f"""Create a {tone} {content_type} about {topic}.

Key points to include:
{key_points}

{format_instructions}

Additional requirements:
- Maintain a {tone} tone throughout
- Use clear and concise language
- Include relevant keywords naturally
- Ensure content is engaging and valuable to the target audience"""
                
                print(f"[DEBUG] Calling OpenAI API...")
                
                try:
                    # Call OpenAI API with GPT-4
                    response = client.chat.completions.create(
                        model="gpt-4-1106-preview",  # Using the latest GPT-4 Turbo
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=0.7,  # Balanced creativity and consistency
                        max_tokens=2000,  # Adjust based on content type
                        top_p=0.9,
                        frequency_penalty=0.3,  # Reduce repetition
                        presence_penalty=0.3    # Encourage diverse content
                    )
                    
                    print("[DEBUG] OpenAI API call successful")
                    generated_content = response.choices[0].message.content.strip()
                    print(f"[DEBUG] Generated content length: {len(generated_content)}")
                    
                    return JsonResponse({'content': generated_content})
                    
                except Exception as e:
                    print(f"[ERROR] OpenAI API Error: {str(e)}")
                    logger.error(f"OpenAI API Error: {str(e)}")
                    logger.error(traceback.format_exc())
                    return JsonResponse({
                        'error': 'An error occurred while generating content.',
                        'details': str(e)
                    }, status=500)
                
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON Decode Error: {str(e)}")
                logger.error(f"JSON Decode Error: {str(e)}")
                return JsonResponse({
                    'error': 'Invalid request format',
                    'details': str(e)
                }, status=400)
                
            except Exception as e:
                print(f"[ERROR] Unexpected Error: {str(e)}")
                logger.error(f"Unexpected Error: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'error': 'An unexpected error occurred',
                    'details': str(e)
                }, status=500)
        
        # Regular page load
        print("[DEBUG] Regular page load - rendering template")
        return render(request, 'founder_assistance/project_content_generator.html', {
            'project': project
        })
        
    except Exception as e:
        print(f"[ERROR] View-level Exception: {str(e)}")
        logger.error(f"View-level Exception: {str(e)}")
        logger.error(traceback.format_exc())
        if request.method == "POST":
            return JsonResponse({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=500)
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)

@login_required
@require_http_methods(["GET", "POST"])
def project_market_analysis(request, project_id):
    """Handle market analysis generation"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user has permission to view
        if project.creator != request.user and request.user not in project.team_members.all():
            messages.error(request, "You don't have permission to view this project's market analysis.")
            return redirect('founder_assistance:project_detail', project_id=project_id)
        
        # Handle AJAX request for analysis generation
        if request.method == "POST" and request.GET.get('generate') == 'true':
            try:
                # Generate and store the analysis
                analysis_result = generate_market_analysis(project)
                
                # Parse the result to ensure it's valid JSON
                try:
                    if isinstance(analysis_result, str):
                        # Try to extract JSON from markdown code block if present
                        if "```json" in analysis_result:
                            json_str = analysis_result.split("```json")[1].split("```")[0].strip()
                            parsed_result = json.loads(json_str)
                        else:
                            parsed_result = json.loads(analysis_result)
                    else:
                        parsed_result = analysis_result

                    # Clean up the data structure if needed
                    if isinstance(parsed_result, dict) and "market_analysis" in parsed_result:
                        parsed_result = parsed_result["market_analysis"]

                    # Update the project's JSON data
                    project.ai_response_json = parsed_result
                    project.save()

                    print("\nMarket Analysis Data Saved to Database:")
                    print("----------------------------------------")
                    print(json.dumps(project.ai_response_json, indent=2))
                    print("----------------------------------------\n")

                    return JsonResponse({'result': parsed_result})
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    return JsonResponse({'error': 'Invalid JSON format in analysis result'}, status=500)

            except Exception as e:
                logger.error(f"Market analysis generation error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
        
        # Regular page load - include stored analysis if available
        context = {
            'project': project,
            'analysis_result': project.ai_response_json
        }
        return render(request, 'founder_assistance/project_market_analysis.html', context)
        
    except Exception as e:
        logger.error(f"Market analysis view error: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)

@login_required
@require_http_methods(["GET", "POST"])
def project_competitor_analysis(request, project_id):
    """Handle competitor analysis generation"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user has permission to view
        if project.creator != request.user and request.user not in project.team_members.all():
            messages.error(request, "You don't have permission to view this project's competitor analysis.")
            return redirect('founder_assistance:project_detail', project_id=project_id)
        
        # Handle AJAX request for analysis generation
        if request.method == "POST" and request.GET.get('generate') == 'true':
            try:
                # Generate the analysis
                analysis_result = generate_competitor_analysis(project)
                
                # Print the saved data to terminal
                print("\nCompetitor Analysis Data Saved to Database:")
                print("----------------------------------------")
                print(json.dumps(project.ai_response_json, indent=2))
                print("----------------------------------------\n")
                
                if isinstance(analysis_result, dict) and 'error' in analysis_result:
                    return JsonResponse({'error': analysis_result['error']}, status=500)
                    
                return JsonResponse({'result': 'success'})
            except Exception as e:
                logger.error(f"Competitor analysis generation error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
        
        # Regular page load
        return render(request, 'founder_assistance/project_competitor_analysis.html', {
            'project': project
        })
    except Exception as e:
        logger.error(f"Competitor analysis view error: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
