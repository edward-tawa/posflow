from activity_log.services.activity_log_service import ActivityLogService
from django.contrib.contenttypes.models import ContentType

def log_activity(instance, action: str, user=None, metadata=None, description=None):
    """
    Centralized function to create an activity log entry
    """
    ActivityLogService.create_activity_log(
        user_id=getattr(user, "id", None),
        action=action,
        content_type=ContentType.objects.get_for_model(instance) if instance else None,
        object_id=instance.id if instance else None,
        metadata=metadata or {},
        description=description or f"{action} on {instance}"
    )