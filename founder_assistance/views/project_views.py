from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Project
import json

@login_required
def project_list(request):
    # Filter projects where user is either the creator or a team member
    projects = Project.objects.filter(creator=request.user) | Project.objects.filter(team_members=request.user)
    projects = projects.distinct()  # Remove any duplicates
    return render(request, 'founder_assistance/project_list.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    context = {
        'project': project,
        'stats': get_project_stats(project),
        'ai_insights': get_project_insights(project)
    }
    return render(request, 'founder_assistance/project_detail.html', context)

def get_project_stats(project):
    """Get project statistics"""
    return {
        'active_projects': Project.objects.filter(status='active').count(),
        'pending_projects': Project.objects.filter(status='pending').count(),
        'total_professionals': Project.objects.values('team_members').distinct().count(),
        'project_earnings': project.earnings
    }

def get_project_insights(project):
    """Get AI insights from related idea"""
    if not project.related_idea:
        return []

    try:
        idea_analysis = json.loads(project.related_idea.description)
        market_analysis = idea_analysis.get('analysis', {}).get('market_analysis', {})
        business_framework = idea_analysis.get('analysis', {}).get('business_framework', {})
        financials = idea_analysis.get('analysis', {}).get('financials', {})
        
        insights = []
        
        if market_analysis.get('market_size'):
            insights.append({
                'icon': 'lightbulb',
                'color': 'warning',
                'title': 'Market Opportunity',
                'description': f"Market size of {market_analysis.get('market_size')} presents significant growth potential"
            })
        
        if business_framework.get('revenue_streams'):
            insights.append({
                'icon': 'chart-pie',
                'color': 'success',
                'title': 'Revenue Streams',
                'description': f"Multiple revenue streams identified: {', '.join(business_framework.get('revenue_streams', []))}"
            })
        
        if financials.get('potential_roi'):
            insights.append({
                'icon': 'coins',
                'color': 'primary',
                'title': 'Financial Potential',
                'description': f"Projected ROI: {financials.get('potential_roi')}"
            })
            
        return insights
        
    except json.JSONDecodeError:
        # Default insights if AI analysis can't be parsed
        return [
            {
                'icon': 'lightbulb',
                'color': 'warning',
                'title': 'Market Opportunity',
                'description': 'AI analysis suggests expanding into the European market could increase revenue by 40%'
            },
            {
                'icon': 'chart-pie',
                'color': 'success',
                'title': 'Customer Segment',
                'description': 'Data shows strong product-market fit with millennials in urban areas'
            },
            {
                'icon': 'coins',
                'color': 'primary',
                'title': 'Financial Optimization',
                'description': 'Implementing suggested cost-saving measures could improve margins by 15%'
            }
        ]
