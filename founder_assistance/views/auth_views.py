from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import SignUpForm, LoginForm

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
