from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Idea, Project, ProjectTimeline

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-transparent',
            'placeholder': 'Email'
        })
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-transparent',
            'placeholder': 'Tell us about yourself',
            'rows': 3
        }),
        required=False
    )
    expertise = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-transparent',
            'placeholder': 'Your areas of expertise'
        })
    )
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'bio', 'expertise', 'profile_image')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control bg-transparent',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control bg-transparent',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control bg-transparent',
            'placeholder': 'Confirm Password'
        })

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Enter your idea title',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Describe your idea in detail. Include the problem it solves and how it works.',
                'rows': 4,
                'required': 'required'
            }),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'status', 'progress',
            'budget', 'start_date', 'end_date', 'team_members',
            'related_idea'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class ProjectTimelineForm(forms.ModelForm):
    class Meta:
        model = ProjectTimeline
        fields = ['title', 'description', 'event_time', 'leader', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'event_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
