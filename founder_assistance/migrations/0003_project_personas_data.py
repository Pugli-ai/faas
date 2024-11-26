from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('founder_assistance', '0002_project_ai_response_json_project_ai_response_raw'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='personas_data',
            field=models.TextField(blank=True, null=True, help_text='JSON data for user personas'),
        ),
    ]
