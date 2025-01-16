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
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-transparent',
            'placeholder': 'Email',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-transparent',
            'placeholder': 'Password',
            'autocomplete': 'off'
        })
    )

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
            'budget', 'earnings', 'start_date', 'end_date', 
            'team_members', 'related_idea'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'placeholder': 'Enter project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'rows': 4,
                'placeholder': 'Describe your project in detail'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select form-select-lg form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Select status'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'min': '0',
                'max': '100',
                'step': '1',
                'placeholder': 'Enter progress percentage'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter project budget'
            }),
            'earnings': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter project earnings'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control form-control-lg form-control-solid',
                'type': 'date'
            }),
            'team_members': forms.SelectMultiple(attrs={
                'class': 'form-select form-select-lg form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Select team members',
                'data-allow-clear': 'true',
                'multiple': 'multiple'
            }),
            'related_idea': forms.Select(attrs={
                'class': 'form-select form-select-lg form-select-solid',
                'data-control': 'select2',
                'data-placeholder': 'Select related idea',
                'data-allow-clear': 'true'
            }),
        }

class ProjectTimelineForm(forms.ModelForm):
    class Meta:
        model = ProjectTimeline
        fields = ['title', 'description', 'event_time', 'leader', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'event_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
