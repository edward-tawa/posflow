from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_return_model import SalesReturn
from sales.serializers.sales_return_serializer import SalesReturnSerializer
from sales.services.sales_return_service import SalesReturnService
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesReturnViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Returns.
    Supports listing, retrieving, creating, updating, and deleting sales returns.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesReturn.objects.all()
    serializer_class = SalesReturnSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['return_number', 'sale_order__order_number', 'customer__first_name', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'return_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesReturn queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesReturn)
                .select_related('company', 'branch', 'customer', 'sale_order')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesReturn instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sales_return = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesReturn '{sales_return.return_number}' created by '{actor}' "
            f"for company '{sales_return.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesReturn instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sales_return = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesReturn '{sales_return.return_number}' updated by '{actor}' "
            f"for company '{sales_return.company.name}'."
        )

    

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        sales_return = self.get_object()
        new_status = request.data.get("new_status")
        if not new_status:
            return Response({"detail": "new_status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_return = SalesReturnService.update_sales_return_status(sales_return, new_status)
            serializer = self.get_serializer(updated_return)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating sales return status: {str(e)}")
            return Response({"detail": "Error updating status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
