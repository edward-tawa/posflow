from activity_log.services.activity_log_service import ActivityLogService
from django.contrib.contenttypes.models import ContentType
from config.middleware.get_current_user_middleware import get_current_user
from users.models.user_model import User

def log_activity(*, company, branch, instance, action: str, user=None, metadata=None, description=None):
    """
    Centralized function to create an activity log entry
    """

    current_user = get_current_user()
    if isinstance(current_user, User):
        user_field = current_user
    else:
        user_field = None
    ActivityLogService.create_activity_log(
        company=company,
        branch=branch,
        user_id=getattr(user, "id", None),
        action=action,
        content_type=ContentType.objects.get_for_model(instance) if instance else None,
        object_id=instance.id if instance else None,
        metadata=metadata or {},
        description=description or f"{action} on {instance}"
    )