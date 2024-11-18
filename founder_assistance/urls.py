from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views.project_base_views import (
    project_list, project_detail, project_edit
)
from .views.project_team_views import (
    add_team_member, remove_team_member
)
from .views.project_ai_views import (
    project_content_generator,
    project_market_analysis,
    project_competitor_analysis
)

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
    path('project/<int:project_id>/', project_detail, name='project_detail'),
    path('project/<int:project_id>/edit/', project_edit, name='project_edit'),
    
    # Project Team URLs
    path('project/<int:project_id>/add-member/', add_team_member, name='add_team_member'),
    path('project/<int:project_id>/remove-member/<int:user_id>/', remove_team_member, name='remove_team_member'),
    
    # Project AI URLs
    path('project/<int:project_id>/generate-content/', project_content_generator, name='project_content_generator'),
    path('project/<int:project_id>/market-analysis/', project_market_analysis, name='project_market_analysis'),
    path('project/<int:project_id>/competitor-analysis/', project_competitor_analysis, name='project_competitor_analysis'),
    
    path('resources/', views.resources, name='resources'),
]
