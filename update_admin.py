from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.get(username='admin')
admin_user.role = 'Admin'
admin_user.save()
