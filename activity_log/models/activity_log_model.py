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

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text='The company context of the activity.',
        null=True,
        blank=True
    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text='The branch context of the activity.',
        null=True,       # allow nulls in DB
        blank=True       # allow blank in forms/admin
    )


    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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

    @staticmethod
    def __str__(self):
        username = self.user.username if self.user else "Deleted User"
        return f"{username} - {self.action} at {self.created_at}"
