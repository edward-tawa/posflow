from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_payment_model import SalesPayment
from sales.serializers.sales_payment_serializer import SalesPaymentSerializer
from loguru import logger


class SalesPaymentViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Payments.
    Supports listing, retrieving, creating, updating, and deleting sales payments.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'payment_number',
        'sales_order__order_number',
        'branch__name',
        'company__name',
        'processed_by__username'
    ]
    ordering_fields = ['created_at', 'updated_at', 'amount', 'payment_date']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesPayment queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesPayment)
                .select_related('sales_order')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesPayment instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesPayment '{payment.payment.payment_number}' for order '{payment.sales_order.order_number}' "
            f"created by '{actor}' for company '{payment.sales_order.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesPayment instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesPayment '{payment.payment_number}' updated by '{actor}' "
            f"for company '{payment.company.name}'."
        )
