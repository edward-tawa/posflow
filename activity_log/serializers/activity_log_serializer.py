from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from loguru import logger
from users.models import User
from activity_log.models.activity_log_model import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    user_summary = serializers.SerializerMethodField(read_only=True)
    content_type_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'user',
            'user_summary',
            'action',
            'content_type',
            'content_type_summary',
            'object_id',
            'description',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
        ]

    def get_user_summary(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
            }
        return None

    def get_content_type_summary(self, obj):
        if obj.content_type:
            return {
                'id': obj.content_type.id,
                'model': obj.content_type.model,
                'app_label': obj.content_type.app_label,
            }
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # Auto-fill user if not provided
        if not validated_data.get('user') and user:
            validated_data['user'] = user

        try:
            activity = ActivityLog.objects.create(**validated_data)
            actor = getattr(activity.user, 'username', 'Unknown')
            logger.info(f"Activity '{activity.action}' logged by {actor}.")
            return activity
        except Exception as e:
            actor = getattr(user, 'username', 'Unknown')
            logger.error(f"Error logging activity by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while logging the activity.")

    
    def update(self, instance, validated_data):
        # Normally activity logs are immutable; optionally raise error
        raise serializers.ValidationError("Activity logs cannot be updated once created.")
