from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ..models import Project, ProjectTimeline
from django.views.decorators.http import require_http_methods
from django.utils.timezone import make_aware
from datetime import datetime

@login_required
@require_http_methods(["POST"])
def add_project_event(request):
    try:
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user is project creator or team member
        if request.user != project.creator and not project.team_members.filter(id=request.user.id).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to add events to this project'
            }, status=403)
        
        # Create the event
        event = ProjectTimeline.objects.create(
            project=project,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            event_time=make_aware(datetime.fromisoformat(request.POST.get('event_time'))),
            leader=request.user,
            status='pending'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Event added successfully',
            'event': {
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_time': event.event_time.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
