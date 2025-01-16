from django.shortcuts import render

def about(request):
    return render(request, 'founder_assistance/about.html')

def support(request):
    return render(request, 'founder_assistance/support.html')

def contact(request):
    return render(request, 'founder_assistance/contact.html')
