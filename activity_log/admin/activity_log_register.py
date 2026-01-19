from django.contrib import admin
from activity_log.models.activity_log_model import ActivityLog


class ActivityLogAdmin(admin.ModelAdmin):
    model = ActivityLog

    list_display = [
        'user',
        'action',
        'metadata'
    ]

    list_filter = [
        'user'
    ]
admin.site.register(ActivityLog, ActivityLogAdmin)