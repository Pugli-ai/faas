from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from ..models import Project
from ..utils import generate_competitor_analysis
import json
import logging
import traceback

logger = logging.getLogger(__name__)

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
                
                if isinstance(analysis_result, dict):
                    if 'error' in analysis_result:
                        return JsonResponse({
                            'error': analysis_result['error'],
                            'details': analysis_result.get('details', '')
                        }, status=500)
                    return JsonResponse({'result': analysis_result})
                return JsonResponse({'error': 'Invalid analysis result format'}, status=500)
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
