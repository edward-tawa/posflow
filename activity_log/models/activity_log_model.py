from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from config.models.create_update_base_model import CreateUpdateBaseModel
from django.utils import timezone
from loguru import logger




class ActivityLog(CreateUpdateBaseModel):
    """
    POSFlow Activity Log: Immutable audit log for user actions.
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs',
        help_text='The user who performed the action.'
    )
    action = models.CharField(
        max_length=50,
        help_text='Precise action performed (service-layer controlled).'
    )

    # -----------------------
    # Action target (Generic)
    # -----------------------
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The type of the object the action was performed on.'
    )
    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text='The ID of the object the action was performed on.'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    description = models.TextField(
        help_text='Human-readable description of the activity.'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra structured data for auditing (amounts, old/new values, reason)"
    )

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Deleted User"
        return f"{username} - {self.action} at {self.created_at}"
