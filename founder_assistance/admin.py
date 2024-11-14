from django.contrib import admin
from .models import Idea, Project, ProjectTimeline

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
    )

@admin.register(ProjectTimeline)
class ProjectTimelineAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'event_time', 'leader', 'status')
    list_filter = ('status', 'event_time', 'created_at')
    search_fields = ('title', 'description', 'project__title', 'leader__username')
    date_hierarchy = 'event_time'
