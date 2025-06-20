# Generated by Django 5.2.1 on 2025-06-12 13:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_comment_notification_tasklog_taskfollower'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='tasklog',
            old_name='timestamp',
            new_name='changed_at',
        ),
        migrations.RemoveField(
            model_name='task',
            name='created_at',
        ),
        migrations.AddField(
            model_name='task',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.comment'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.task'),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='field_changed',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='taskfollower',
            unique_together={('task', 'user')},
        ),
    ]
