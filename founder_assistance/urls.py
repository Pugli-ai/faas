from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'founder_assistance'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='founder_assistance:home'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('ideas/', views.idea_list, name='idea_list'),
    path('ideas/create/', views.idea_create, name='idea_create'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('resources/', views.resources, name='resources'),
]
