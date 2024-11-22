from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from ..models import Project
from ..utils import generate_market_analysis, generate_competitor_analysis
import json
import logging
import traceback

logger = logging.getLogger(__name__)

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
                
                try:
                    # Return the stored JSON data from the model
                    if project.ai_response_json:
                        return JsonResponse({'result': project.ai_response_json})
                    else:
                        logger.error("No analysis data saved to model")
                        return JsonResponse({'error': 'No analysis data generated'}, status=500)

                except Exception as e:
                    logger.error(f"Error returning analysis data: {str(e)}")
                    return JsonResponse({'error': 'Error processing analysis data'}, status=500)

            except Exception as e:
                logger.error(f"Market analysis generation error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
        
        # Regular page load - pass the JSON data directly
        try:
            if project.ai_response_json:
                # Pass the JSON data directly without additional serialization
                analysis_json = project.ai_response_json
                logger.info("Successfully retrieved analysis data")
                logger.debug(f"Analysis data: {analysis_json}")
            else:
                analysis_json = None
                logger.info("No analysis data available")
        except Exception as e:
            logger.error(f"Error retrieving analysis data: {str(e)}")
            analysis_json = None
            messages.error(request, "There was an error loading the analysis data. Please try generating a new analysis.")

        context = {
            'project': project,
            'analysis_result': mark_safe(json.dumps(analysis_json)) if analysis_json else None
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
