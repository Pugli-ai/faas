from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import SignUpForm, LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Since USERNAME_FIELD is set to email in the User model,
            # we can directly use email for authentication
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('founder_assistance:home')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'founder_assistance/login.html', {'form': form})

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
