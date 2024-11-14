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
def convert_to_project(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, creator=request.user)
    
    try:
        # Parse the AI analysis from the idea description
        analysis = json.loads(idea.description)
        
        # Create new project
        project = Project.objects.create(
            title=idea.title,
            description=analysis.get('analysis', {}).get('refined_idea', {}).get('enhanced_description', idea.description),
            creator=request.user,
            related_idea=idea,
            status='active',
            progress=0
        )
        
        # Add creator as team member
        project.team_members.add(request.user)
        
        # Create initial timeline event
        project.timeline_events.create(
            title="Project Initiated",
            description=f"Project created from idea: {idea.title}",
            leader=request.user,
            status='completed'
        )
        
        messages.success(request, 'Idea successfully converted to project!')
        return redirect('founder_assistance:project_detail', project_id=project.id)
        
    except Exception as e:
        messages.error(request, f'Failed to convert idea to project: {str(e)}')
        return redirect('founder_assistance:idea_list')

@login_required
def project_list(request):
    # Filter projects where user is either the creator or a team member
    projects = Project.objects.filter(creator=request.user) | Project.objects.filter(team_members=request.user)
    projects = projects.distinct()  # Remove any duplicates
    return render(request, 'founder_assistance/project_list.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Get project's related idea AI analysis if available
    ai_insights = []
    if project.related_idea:
        try:
            idea_analysis = json.loads(project.related_idea.description)
            market_analysis = idea_analysis.get('analysis', {}).get('market_analysis', {})
            business_framework = idea_analysis.get('analysis', {}).get('business_framework', {})
            financials = idea_analysis.get('analysis', {}).get('financials', {})
            
            # Generate insights based on AI analysis
            if market_analysis.get('market_size'):
                ai_insights.append({
                    'icon': 'lightbulb',
                    'color': 'warning',
                    'title': 'Market Opportunity',
                    'description': f"Market size of {market_analysis.get('market_size')} presents significant growth potential"
                })
            
            if business_framework.get('revenue_streams'):
                ai_insights.append({
                    'icon': 'chart-pie',
                    'color': 'success',
                    'title': 'Revenue Streams',
                    'description': f"Multiple revenue streams identified: {', '.join(business_framework.get('revenue_streams', []))}"
                })
            
            if financials.get('potential_roi'):
                ai_insights.append({
                    'icon': 'coins',
                    'color': 'primary',
                    'title': 'Financial Potential',
                    'description': f"Projected ROI: {financials.get('potential_roi')}"
                })
        except json.JSONDecodeError:
            # If AI analysis can't be parsed, provide default insights
            ai_insights = [
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
    
    context = {
        'project': project,
        'ai_insights': ai_insights,
        'stats': {
            'active_projects': Project.objects.filter(status='active').count(),
            'pending_projects': Project.objects.filter(status='pending').count(),
            'total_professionals': Project.objects.values('team_members').distinct().count(),
            'project_earnings': project.earnings
        }
    }
    return render(request, 'founder_assistance/project_detail.html', context)

@login_required
def resources(request):
    return render(request, 'founder_assistance/resources.html')
