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
from rest_framework.decorators import action
from rest_framework.response import Response
from activity_log.services.activity_log_service import ActivityLogService
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



    @action(detail=False, methods=["get"], url_path="filter")
    def filter_logs(self, request):
        filters = {}

        if user_id := request.query_params.get("user_id"):
            filters["user_id"] = user_id

        if action_name := request.query_params.get("action"):
            filters["action"] = action_name

        if object_type := request.query_params.get("object_type"):
            filters["object_type"] = object_type

        if object_id := request.query_params.get("object_id"):
            filters["object_id"] = object_id

        queryset = ActivityLogService.filter_activity_logs(**filters)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)