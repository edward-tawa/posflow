from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from loguru import logger
from activity_log.models.activity_log_model import ActivityLog
from activity_log.serializers.activity_log_serializer import ActivityLogSerializer
from activity_log.permissions.activity_log_permissions import ActivityLogPermissions


class ActivityLogViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for viewing Activity Logs.
    -------------------
    - Read-only (list & retrieve)
    - No create, update, or delete
    - Used for auditing & monitoring
    -------------------
    """

    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [ActivityLogPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        'action',
        'description',
        'user__username',
        'content_type__model',
    ]

    ordering_fields = [
        'created_at',
        'action',
    ]

    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns Activity Logs filtered by logged-in company.
        -------------------
        """
        try:
            queryset = get_company_queryset(self.request, ActivityLog)

            return queryset.select_related(
                'user',
                'content_type',
            )
        except Exception as e:
            logger.error(f"Error fetching ActivityLog queryset: {e}")
            return ActivityLog.objects.none()
