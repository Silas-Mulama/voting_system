# Generated migration for college/TTI system refactoring
# Removes class_form field and adds programme and year_of_study fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='programme',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='year_of_study',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='user',
            name='class_form',
        ),
    ]
