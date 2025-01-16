from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models import Project
from ..utils.market_analysis import generate_market_analysis
import logging

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
                # Generate the analysis
                logger.info("Starting market analysis generation")
                analysis_result = generate_market_analysis(project)
                logger.info(f"Analysis result received: {analysis_result}")
                
                # Handle error cases
                if isinstance(analysis_result, dict) and 'error' in analysis_result:
                    error_msg = analysis_result['error']
                    details = analysis_result.get('details', '')
                    logger.error(f"Analysis error: {error_msg}")
                    logger.error(f"Error details: {details}")
                    return JsonResponse({
                        'error': error_msg,
                        'details': details
                    }, status=500)
                
                # Save the analysis to the database
                project.market_analysis = analysis_result
                project.save()
                logger.info("Market analysis saved to database")
                
                # Return the markdown result
                logger.info("Preparing to return successful response")
                logger.debug(f"Analysis result: {analysis_result}")
                return JsonResponse({'result': analysis_result})
            except Exception as e:
                error_msg = f"Market analysis generation error: {str(e)}"
                logger.error(error_msg)
                logger.error("Full error traceback:", exc_info=True)
                return JsonResponse({
                    'error': 'Market Analysis Error',
                    'details': error_msg
                }, status=500)
        
        # Regular page load
        return render(request, 'founder_assistance/project_market_analysis.html', {
            'project': project
        })
    except Exception as e:
        logger.error(f"Market analysis view error: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
