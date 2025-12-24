from notifications.models.notification_model import Notification
from django.db import transaction as db_transaction
from loguru import logger


class NotificationService:
    """
    Service layer for Notification domain.
    Handles state changes and lifecycle operations.
    Query logic is delegated to NotificationManager.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_notification(**kwargs) -> Notification:
        required_fields = {"title", "message", "notification_to"}

        missing = required_fields - kwargs.keys()
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        try:
            notification = Notification.objects.create(**kwargs)
            logger.success(f"Notification '{notification.id}' created.")
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_notification(notification: Notification, **kwargs) -> Notification:
        try:
            for key, value in kwargs.items():
                setattr(notification, key, value)

            notification.save(update_fields=kwargs.keys())
            logger.info(f"Notification '{notification.id}' updated.")
            return notification
        except Exception as e:
            logger.error(f"Error updating notification '{notification.id}': {str(e)}")
            raise

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_notification(notification: Notification) -> None:
        try:
            notification_id = notification.id
            notification.delete()
            logger.info(f"Notification '{notification_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting notification '{notification.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_notification_by_id(notification_id: int) -> bool:
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            logger.info(f"Notification '{notification_id}' deleted.")
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification '{notification_id}' not found for deletion.")
            return False
        except Exception as e:
            logger.error(f"Error deleting notification '{notification_id}': {str(e)}")
            raise

    # -------------------------
    # STATE TRANSITIONS
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def mark_as_read(notification: Notification) -> Notification:
        try:
            notification.is_read = True
            notification.status = 'READ'
            notification.save(update_fields=["is_read", "status"])
            logger.info(f"Notification '{notification.id}' marked as read.")
            return notification
        except Exception as e:
            logger.error(f"Error marking notification '{notification.id}' as read: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def mark_as_unread(notification: Notification) -> Notification:
        try:
            notification.is_read = False
            notification.status = 'PENDING'
            notification.save(update_fields=["is_read", "status"])
            logger.info(f"Notification '{notification.id}' marked as unread.")
            return notification
        except Exception as e:
            logger.error(f"Error marking notification '{notification.id}' as unread: {str(e)}")
            raise

    # -------------------------
    # READ OPERATIONS (DELEGATE TO MANAGER)
    # -------------------------
    @staticmethod
    def get_notification_by_id(notification_id: int) -> Notification | None:
        try:
            return Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            logger.warning(f"Notification '{notification_id}' not found.")
            return None
        except Exception as e:
            logger.error(f"Error fetching notification '{notification_id}': {str(e)}")
            raise

    @staticmethod
    def get_notifications_for_user(user_id: int):
        return Notification.objects.for_user(user_id).order_by('-created_at')

    @staticmethod
    def get_unread_notifications_for_user(user_id: int):
        return (
            Notification.objects
            .for_user(user_id)
            .unread()
            .order_by('-created_at')
        )

    @staticmethod
    def get_read_notifications_for_user(user_id: int):
        return (
            Notification.objects
            .for_user(user_id)
            .filter(is_read=True)
            .order_by('-created_at')
        )

    # -------------------------
    # COUNTS
    # -------------------------
    @staticmethod
    def count_unread_notifications_for_user(user_id: int) -> int:
        return Notification.objects.for_user(user_id).unread().count()

    @staticmethod
    def count_read_notifications_for_user(user_id: int) -> int:
        return Notification.objects.for_user(user_id).filter(is_read=True).count()

    @staticmethod
    def count_all_notifications_for_user(user_id: int) -> int:
        return Notification.objects.for_user(user_id).count()

    # -------------------------
    # BULK DELETES
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_notifications_for_user(user_id: int) -> int:
        deleted_count, _ = Notification.objects.for_user(user_id).delete()
        logger.info(f"Deleted {deleted_count} notifications for user '{user_id}'.")
        return deleted_count

    @staticmethod
    @db_transaction.atomic
    def delete_read_notifications_for_user(user_id: int) -> int:
        deleted_count, _ = (
            Notification.objects
            .for_user(user_id)
            .filter(is_read=True)
            .delete()
        )
        logger.info(f"Deleted {deleted_count} read notifications for user '{user_id}'.")
        return deleted_count

    @staticmethod
    @db_transaction.atomic
    def delete_unread_notifications_for_user(user_id: int) -> int:
        deleted_count, _ = (
            Notification.objects
            .for_user(user_id)
            .unread()
            .delete()
        )
        logger.info(f"Deleted {deleted_count} unread notifications for user'{user_id}'.")
        return deleted_count
