from .auth_views import login_view, signup_view, profile_view
from .idea_views import idea_list, idea_create, convert_to_project, idea_delete
from .project_views import project_list, project_detail
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractWeekDay
from django.utils import timezone
from datetime import timedelta
from ..models import Idea, Project, User

def home(request):
    # Get total ideas
    total_ideas = Idea.objects.count()
    
    # Get projects stats
    total_projects = Project.objects.filter(status='active').count()
    pending_ideas = Project.objects.filter(status='pending').count()
    
    # Calculate completion rate
    total_projects_all = Project.objects.count()
    completed_projects = Project.objects.filter(status='completed').count()
    completion_rate = int((completed_projects / total_projects_all * 100) if total_projects_all > 0 else 0)
    
    # Get active users (users who are team members in active projects)
    active_users = User.objects.filter(project_teams__status='active').distinct()

    # Get monthly data for charts
    current_year = timezone.now().year
    monthly_ideas = (
        Idea.objects.filter(created_at__year=current_year)
        .annotate(month=ExtractMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    monthly_projects = (
        Project.objects.filter(created_at__year=current_year)
        .annotate(month=ExtractMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Initialize monthly data arrays with zeros
    monthly_ideas_data = [0] * 12
    monthly_projects_data = [0] * 12
    
    # Fill in the actual counts
    for item in monthly_ideas:
        monthly_ideas_data[item['month'] - 1] = item['count']
    for item in monthly_projects:
        monthly_projects_data[item['month'] - 1] = item['count']

    # Get weekly data (last 7 days)
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    
    weekly_ideas = (
        Idea.objects.filter(created_at__gte=week_ago)
        .annotate(day=ExtractWeekDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    weekly_projects = (
        Project.objects.filter(created_at__gte=week_ago)
        .annotate(day=ExtractWeekDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Initialize weekly data arrays with zeros
    weekly_ideas_data = [0] * 7
    weekly_projects_data = [0] * 7
    
    # Fill in the actual counts
    for item in weekly_ideas:
        # Convert to 0-based index (Sunday = 0)
        day_index = item['day'] % 7
        weekly_ideas_data[day_index] = item['count']
    for item in weekly_projects:
        day_index = item['day'] % 7
        weekly_projects_data[day_index] = item['count']

    context = {
        'total_ideas': total_ideas,
        'total_projects': total_projects,
        'pending_ideas': pending_ideas,
        'completion_rate': completion_rate,
        'active_users': active_users,
        'monthly_data': {
            'ideas': monthly_ideas_data,
            'projects': monthly_projects_data,
        },
        'weekly_data': {
            'ideas': weekly_ideas_data,
            'projects': weekly_projects_data,
        }
    }
    
    return render(request, 'founder_assistance/home.html', context)

def resources(request):
    return render(request, 'founder_assistance/resources.html')
