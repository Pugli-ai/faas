from django.apps import AppConfig

class FounderAssistanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'founder_assistance'

    def ready(self):
        # This ensures template tags are loaded when the app starts
        import founder_assistance.templatetags.idea_filters
