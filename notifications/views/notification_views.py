from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.pagination.pagination import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from loguru import logger
from django.db.models import Q

from notifications.models.notification_model import Notification
from notifications.serializers.notification_serializer import NotificationSerializer
from notification.services.notification_service import NotificationService  # optional service layer
from users.models import User
from notifications.permissions.notification_permissions import NotificationPermission  # create as needed


class NotificationViewSet(ModelViewSet):
    """
    ViewSet for managing Notifications.
    Supports listing, retrieving, creating, updating, and deleting notifications.
    Includes filtering, searching, ordering, and logging.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [NotificationPermission]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'title',
        'message',
        'notification_to__username',
        'notification_from_content_type__model'
    ]
    ordering_fields = ['created_at', 'status', 'is_read']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns notifications filtered by the logged-in user.
        -------------------
        """
        try:
            user = self.request.user
            return Notification.objects.filter(notification_to=user).select_related(
                'notification_to',
                'notification_from_content_type'
            )
        except Exception as e:
            logger.error(f"Error fetching Notifications queryset: {e}")
            return Notification.objects.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new Notification instance and logs the event.
        -------------------
        """
        user = self.request.user
        notification = serializer.save()
        actor = getattr(user, 'username', 'Unknown')

        logger.success(
            f"Notification '{notification.id}' created by '{actor}' "
            f"for user '{notification.notification_to.username}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated Notification instance and logs the event.
        -------------------
        """
        user = self.request.user
        notification = serializer.save()
        actor = getattr(user, 'username', 'Unknown')

        logger.info(
            f"Notification '{notification.id}' updated by '{actor}' "
            f"for user '{notification.notification_to.username}'."
        )

    # -------------------------
    # Custom action methods
    # -------------------------

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        Marks a notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.status = 'READ'
        notification.save()
        logger.info(f"Notification '{notification.id}' marked as READ by '{request.user.username}'.")
        return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-unread')
    def mark_unread(self, request, pk=None):
        """
        Marks a notification as unread.
        """
        notification = self.get_object()
        notification.is_read = False
        notification.status = 'PENDING'
        notification.save()
        logger.info(f"Notification '{notification.id}' marked as UNREAD by '{request.user.username}'.")
        return Response({'status': 'Notification marked as unread'}, status=status.HTTP_200_OK)
