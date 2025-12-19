from activity_log.models.activity_log_model import ActivityLog
from django.db import transaction
from django.db.models import QuerySet
from loguru import logger


class ActivityLogService:
    """
    Service layer for Activity Log domain operations.
    Handles creation and retrieval of activity logs in a safe,
    ordered, and domain-consistent manner.
    """

    REQUIRED_FIELDS = {"user_id", "action"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_activity_log(**kwargs) -> ActivityLog:
        missing_fields = ActivityLogService.REQUIRED_FIELDS - kwargs.keys()
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        activity_log = ActivityLog.objects.create(**kwargs)

        logger.info(
            "Activity log created | id={} | action={} | user_id={}",
            activity_log.id,
            activity_log.action,
            activity_log.user_id,
        )

        return activity_log

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_activity_log_by_id(activity_log_id: int) -> ActivityLog | None:
        try:
            return ActivityLog.objects.get(id=activity_log_id)
        except ActivityLog.DoesNotExist:
            logger.warning("Activity log not found | id={}", activity_log_id)
            return None

    @staticmethod
    def list_activity_logs_by_user(user_id: int) -> QuerySet[ActivityLog]:
        return (
            ActivityLog.objects
            .filter(user_id=user_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def list_activity_logs_by_action(action: str) -> QuerySet[ActivityLog]:
        return (
            ActivityLog.objects
            .filter(action=action)
            .order_by("-timestamp")
        )

    @staticmethod
    def list_activity_logs_by_object(
        object_type: str,
        object_id: int
    ) -> QuerySet[ActivityLog]:
        return (
            ActivityLog.objects
            .filter(object_type=object_type, object_id=object_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def list_activity_logs_by_date_range(
        start_date,
        end_date
    ) -> QuerySet[ActivityLog]:
        return (
            ActivityLog.objects
            .filter(timestamp__gte=start_date, timestamp__lte=end_date)
            .order_by("-timestamp")
        )

    @staticmethod
    def list_all_activity_logs() -> QuerySet[ActivityLog]:
        return ActivityLog.objects.all().order_by("-timestamp")

    # -------------------------
    # FLEXIBLE FILTER
    # -------------------------
    @staticmethod
    def filter_activity_logs(**filters) -> QuerySet[ActivityLog]:
        """
        Generic filter method for advanced querying.
        Example:
            filter_activity_logs(user_id=1, action="CREATE")
        """
        return ActivityLog.objects.filter(**filters).order_by("-timestamp")
