from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    expertise = models.CharField(max_length=100, blank=True, null=True)  # Added null=True
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Idea(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  # Added null=True
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  # Added null=True
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.IntegerField(default=0)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_date = models.DateTimeField(default=timezone.now)  # Added default
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects', null=True)
    team_members = models.ManyToManyField(User, related_name='project_teams')
    related_idea = models.ForeignKey(Idea, on_delete=models.SET_NULL, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_progress_percentage(self):
        return f"{self.progress}%"

    def get_status_display_class(self):
        status_classes = {
            'active': 'badge-light-primary',
            'pending': 'badge-light-warning',
            'completed': 'badge-light-success',
            'on_hold': 'badge-light-danger',
        }
        return status_classes.get(self.status, 'badge-light-info')

class ProjectTimeline(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timeline_events')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)  # Added null=True
    event_time = models.DateTimeField(default=timezone.now)  # Added default
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_time']

    def __str__(self):
        return f"{self.project.title} - {self.title}"
