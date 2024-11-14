from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, LoginForm, IdeaForm
from .models import Idea, Project
from .utils import augment_idea_with_ai
import json

def home(request):
    return render(request, 'founder_assistance/home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('founder_assistance:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'founder_assistance/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('founder_assistance:home')
    else:
        form = SignUpForm()
    return render(request, 'founder_assistance/signup.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'founder_assistance/profile.html', {'user': request.user})

@login_required
def idea_list(request):
    ideas = Idea.objects.filter(creator=request.user)
    return render(request, 'founder_assistance/idea_list.html', {'ideas': ideas})

@login_required
def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            # Create idea but don't save to DB yet
            idea = form.save(commit=False)
            idea.creator = request.user
            
            # Get the original title and description
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            
            # Use OpenAI to augment the idea
            try:
                augmented_data = augment_idea_with_ai(title, description)
                # Parse the JSON string back to a dictionary
                analysis = json.loads(augmented_data)
                
                # Update the description with the augmented analysis
                idea.description = augmented_data
                idea.save()
                
                messages.success(request, 'Idea created successfully with AI-enhanced analysis!')
            except Exception as e:
                # If AI augmentation fails, save the original idea
                idea.save()
                messages.warning(request, f'Idea saved with original description. AI enhancement failed: {str(e)}')
            
            return redirect('founder_assistance:idea_list')
    else:
        form = IdeaForm()
    return render(request, 'founder_assistance/idea_form.html', {'form': form})

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
        'stats': {
            'active_projects': Project.objects.filter(status='active').count(),
            'pending_projects': Project.objects.filter(status='pending').count(),
            'total_professionals': 357,  # This should be replaced with actual data
            'project_earnings': 69700,  # This should be replaced with actual data
        },
        'timeline_events': [
            {
                'time': '10:20 - 11:00',
                'period': 'AM',
                'description': '9 Degree Project Estimation Meeting',
                'leader': 'Peter Marcus',
                'status': 'success'
            },
            # Add more timeline events as needed
        ]
    }
    return render(request, 'founder_assistance/project_detail.html', context)

@login_required
def resources(request):
    return render(request, 'founder_assistance/resources.html')
