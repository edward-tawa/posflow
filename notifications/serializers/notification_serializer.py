from notifications.models.notification_model import Notification
from rest_framework import serializers
from loguru import logger
from django.contrib.contenttypes.models import ContentType
from users.models.user_model import User



class NotificationSerializer(serializers.ModelSerializer):
    notification_from_summary = serializers.SerializerMethodField(read_only=True)
    notification_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'notification_from_content_type',
            'notification_from_object_id',
            'notification_from_summary',
            'notification_to',
            'is_read',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
        ]

    def get_notification_from_summary(self, obj):
        """
        Returns a summary of the object sending the notification.
        """
        from_obj = obj.notification_from
        if from_obj:
            return {
                'id': getattr(from_obj, 'id', None),
                'repr': str(from_obj),
                'model': obj.notification_from_content_type.model if obj.notification_from_content_type else None
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        # Ensure notification_to is not the same as sender
        from_obj = attrs.get('notification_from_object_id')
        content_type = attrs.get('notification_from_content_type')
        if from_obj and content_type:
            try:
                model_class = content_type.model_class()
                sender_obj = model_class.objects.get(pk=from_obj)
                if sender_obj == attrs.get('notification_to'):
                    logger.warning(f"{actor} attempted to send a notification to themselves.")
                    raise serializers.ValidationError("You cannot send a notification to yourself.")
            except Exception as e:
                logger.error(f"Error validating notification_from: {e}")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        try:
            notification = Notification.objects.create(**validated_data)
            logger.info(f"Notification '{notification.id}' created by {actor}.")
            return notification
        except Exception as e:
            logger.error(f"Error creating Notification by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the notification.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        # Prevent changing the sender
        validated_data.pop('notification_from_content_type', None)
        validated_data.pop('notification_from_object_id', None)

        instance = super().update(instance, validated_data)
        logger.info(f"Notification '{instance.id}' updated by {actor}.")
        return instance
