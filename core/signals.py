from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Task, TaskLog

@receiver(pre_save, sender=Task)
def log_task_changes(sender, instance, **kwargs):
    if not instance.pk:
        return  # إنشاء جديد، لا حاجة للتسجيل
    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return

    fields = ['title', 'description', 'status', 'due_date', 'assignee_id']
    for field in fields:
        old_value = getattr(old, field)
        new_value = getattr(instance, field)
        if old_value != new_value:
            TaskLog.objects.create(
                task=instance,
                field_changed=field,
                old_value=old_value,
                new_value=new_value,
                changed_by=instance.updated_by  # سنمرّر هذا من view
            )
