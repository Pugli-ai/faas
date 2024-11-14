from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Updates the admin user role'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        try:
            admin_user = User.objects.get(username='admin')
            admin_user.role = 'Admin'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated admin role'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found'))
