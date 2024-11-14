from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..forms import IdeaForm
from ..models import Idea, Project
from ..utils import augment_idea_with_ai
import json

@login_required
def idea_list(request):
    ideas = Idea.objects.filter(creator=request.user)
    form = IdeaForm()  # Create a new form instance for the modal
    return render(request, 'founder_assistance/idea_list.html', {
        'ideas': ideas,
        'form': form  # Pass the form to the template
    })

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
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'idea': {
                            'id': idea.id,
                            'title': idea.title,
                            'description': analysis.get('analysis', {}).get('refined_idea', {}).get('enhanced_description', description)
                        }
                    })
                else:
                    messages.success(request, 'Idea created successfully with AI-enhanced analysis!')
                    return redirect('founder_assistance:idea_list')
            except Exception as e:
                # If AI augmentation fails, save the original idea
                idea.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'warning': f'Idea saved with original description. AI enhancement failed: {str(e)}',
                        'idea': {
                            'id': idea.id,
                            'title': idea.title,
                            'description': description
                        }
                    })
                else:
                    messages.warning(request, f'Idea saved with original description. AI enhancement failed: {str(e)}')
                    return redirect('founder_assistance:idea_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            
    else:
        form = IdeaForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': {'form': 'Invalid request method'}})
    return render(request, 'founder_assistance/idea_form.html', {'form': form})

@login_required
def idea_delete(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, creator=request.user)
    if request.method == 'POST':
        idea.delete()
        messages.success(request, 'Idea deleted successfully!')
    return redirect('founder_assistance:idea_list')

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
