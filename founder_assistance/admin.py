from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Idea, Project, ProjectTimeline

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'expertise', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'expertise')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'bio', 'expertise', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'creator__username')
    date_hierarchy = 'created_at'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'progress', 'budget', 'earnings', 'start_date', 'creator')
    list_filter = ('status', 'created_at', 'start_date')
    search_fields = ('title', 'description', 'creator__username')
    filter_horizontal = ('team_members',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'status', 'progress')
        }),
        ('Financial Information', {
            'fields': ('budget', 'earnings'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Relationships', {
            'fields': ('creator', 'team_members', 'related_idea')
        }),
        ('AI Analysis', {
            'fields': ('ai_response_raw', 'ai_response_json'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProjectTimeline)
class ProjectTimelineAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'event_time', 'leader', 'status')
    list_filter = ('status', 'event_time', 'created_at')
    search_fields = ('title', 'description', 'project__title', 'leader__username')
    date_hierarchy = 'event_time'
