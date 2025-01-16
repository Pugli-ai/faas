from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views.project_base_views import (
    project_list, project_create, project_detail, project_edit
)
from .views.project_team_views import (
    add_team_member, remove_team_member
)
from .views.project_ai_content_views import (
    project_content_generator
)
from .views.project_ai_analysis_views import (
    project_competitor_analysis
)
from .views.project_ai_market_analysis_views import (
    project_market_analysis
)
from .views.project_ai_chat_views import (
    project_legal_chat
)
from .views.project_ai_personas_views import (
    project_user_personas
)
from .views.project_timeline_views import (
    add_project_event
)
from .views.startup_guide_views import (
    startup_guide_overview,
    startup_guide_ideation,
    startup_guide_business_planning,
    startup_guide_legal,
    startup_guide_funding,
    startup_guide_marketing
)
from .views.static_page_views import about, support, contact

app_name = 'founder_assistance'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='founder_assistance:home'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('ideas/', views.idea_list, name='idea_list'),
    path('ideas/create/', views.idea_create, name='idea_create'),
    path('ideas/<int:idea_id>/delete/', views.idea_delete, name='idea_delete'),
    path('ideas/<int:idea_id>/convert/', views.convert_to_project, name='convert_to_project'),
    
    # Project URLs
    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
    path('project/<int:project_id>/', project_detail, name='project_detail'),
    path('project/<int:project_id>/edit/', project_edit, name='project_edit'),
    
    # Project Team URLs
    path('project/<int:project_id>/add-member/', add_team_member, name='add_team_member'),
    path('project/<int:project_id>/remove-member/<int:user_id>/', remove_team_member, name='remove_team_member'),
    
    # Project AI URLs
    path('project/<int:project_id>/generate-content/', project_content_generator, name='project_content_generator'),
    path('project/<int:project_id>/competitor-analysis/', project_competitor_analysis, name='project_competitor_analysis'),
    path('project/<int:project_id>/market-analysis/', project_market_analysis, name='project_market_analysis'),
    path('project/<int:project_id>/legal-chat/', project_legal_chat, name='project_legal_chat'),
    path('project/<int:project_id>/user-personas/', project_user_personas, name='project_user_personas'),
    
    # Project Timeline URLs
    path('project/add-event/', add_project_event, name='add_project_event'),
    
    # Startup Guide URLs
    path('startup-guide/', startup_guide_overview, name='startup_guide_overview'),
    path('startup-guide/ideation/', startup_guide_ideation, name='startup_guide_ideation'),
    path('startup-guide/business-planning/', startup_guide_business_planning, name='startup_guide_business_planning'),
    path('startup-guide/legal/', startup_guide_legal, name='startup_guide_legal'),
    path('startup-guide/funding/', startup_guide_funding, name='startup_guide_funding'),
    path('startup-guide/marketing/', startup_guide_marketing, name='startup_guide_marketing'),
    
    path('resources/', views.resources, name='resources'),
    
    # Static Pages
    path('about/', about, name='about'),
    path('support/', support, name='support'),
    path('contact/', contact, name='contact'),
]
