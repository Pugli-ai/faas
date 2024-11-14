from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .views.auth_views import login_view, signup_view
from .views.idea_views import idea_list, idea_create, idea_delete, convert_to_project
from .views.project_views import project_list, project_detail

@login_required
def home(request):
    return render(request, 'founder_assistance/home.html')

@login_required
def profile_view(request):
    return render(request, 'founder_assistance/profile.html')

@login_required
def resources(request):
    return render(request, 'founder_assistance/resources.html')
