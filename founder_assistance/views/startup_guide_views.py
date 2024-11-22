from django.shortcuts import render

def startup_guide_overview(request):
    return render(request, 'founder_assistance/startup_guide_overview.html', {'active_section': 'overview'})

def startup_guide_ideation(request):
    return render(request, 'founder_assistance/startup_guide_ideation.html', {'active_section': 'ideation'})

def startup_guide_business_planning(request):
    return render(request, 'founder_assistance/startup_guide_business_planning.html', {'active_section': 'business_planning'})

def startup_guide_legal(request):
    return render(request, 'founder_assistance/startup_guide_legal.html', {'active_section': 'legal'})

def startup_guide_funding(request):
    return render(request, 'founder_assistance/startup_guide_funding.html', {'active_section': 'funding'})

def startup_guide_marketing(request):
    return render(request, 'founder_assistance/startup_guide_marketing.html', {'active_section': 'marketing'})
