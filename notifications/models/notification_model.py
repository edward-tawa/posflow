from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from config.models.create_update_base_model import CreateUpdateBaseModel
from django.utils import timezone
from loguru import logger


class NotificationManager(models.Manager):

    def unread(self):
        return self.filter(is_read=False)
    
    def for_user(self, user):
        return self.filter(notification_to=user)
    
    def pending(self):
        return self.filter(status='PENDING')


class Notification(CreateUpdateBaseModel):
    """
    Docstring for Notification
    """
    
    NOTIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('READ', 'Read'),
    ]
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_from_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_contenttype')
    notification_from_object_id = models.PositiveIntegerField(null=True, blank=True)
    notification_from = GenericForeignKey('notification_from_content_type', 'notification_from_object_id')
    notification_to = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=NOTIFICATION_STATUS, default='PENDING')

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification_to', 'is_read']),
            models.Index(fields=['notification_from_content_type', 'notification_from_object_id']),
        ]

    objects = NotificationManager()

    def __str__(self):
        return f"Notification(id={self.id}, title={self.title})"
   
