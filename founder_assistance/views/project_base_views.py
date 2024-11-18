from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Project
from ..forms import ProjectForm
from .project_helpers import get_project_stats, get_project_insights

@login_required
def project_list(request):
    """List all projects where user is either creator or team member"""
    projects = Project.objects.filter(creator=request.user) | Project.objects.filter(team_members=request.user)
    projects = projects.distinct()
    return render(request, 'founder_assistance/project_list.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    """Show detailed view of a project"""
    project = get_object_or_404(Project, id=project_id)
    context = {
        'project': project,
        'stats': get_project_stats(project),
        'ai_insights': get_project_insights(project)
    }
    return render(request, 'founder_assistance/project_detail.html', context)

@login_required
def project_edit(request, project_id):
    """Edit project details"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to edit
    if project.creator != request.user and request.user not in project.team_members.all():
        messages.error(request, "You don't have permission to edit this project.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('founder_assistance:project_detail', project_id=project_id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'founder_assistance/project_form.html', {
        'form': form,
        'project': project,
        'is_edit': True
    })
