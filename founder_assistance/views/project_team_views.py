from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from ..models import Project

@login_required
@require_http_methods(["POST"])
def add_team_member(request, project_id):
    """Add a team member to the project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to add team members
    if project.creator != request.user and request.user not in project.team_members.all():
        messages.error(request, "You don't have permission to add team members to this project.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
    
    email = request.POST.get('email')
    role = request.POST.get('role')
    
    if not email or not role:
        messages.error(request, "Both email and role are required.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
    
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
        if user == project.creator:
            messages.error(request, "The project creator is already a team member.")
        elif user in project.team_members.all():
            messages.error(request, "This user is already a team member.")
        else:
            project.team_members.add(user)
            messages.success(request, f"{user.email} has been added to the project.")
    except User.DoesNotExist:
        messages.error(request, "No user found with this email address.")
    
    return redirect('founder_assistance:project_detail', project_id=project_id)

@login_required
@require_http_methods(["POST"])
def remove_team_member(request, project_id, user_id):
    """Remove a team member from the project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to remove team members
    if project.creator != request.user:
        messages.error(request, "Only the project creator can remove team members.")
        return redirect('founder_assistance:project_detail', project_id=project_id)
    
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        if user in project.team_members.all():
            project.team_members.remove(user)
            messages.success(request, f"{user.email} has been removed from the project.")
        else:
            messages.error(request, "This user is not a team member of this project.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    return redirect('founder_assistance:project_detail', project_id=project_id)
