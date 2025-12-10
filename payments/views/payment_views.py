from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models import Payment
from payments.serializers.payment_serializer import PaymentSerializer
from loguru import logger


class PaymentViewSet(ModelViewSet):
    """
    ViewSet for managing Payments.
    Supports listing, retrieving, creating, updating, and deleting payments.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = []  # Add your custom permissions if needed

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'payment_number',
        'payment_type',
        'company__name',
        'branch__name',
        'paid_by__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'payment_date', 'amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns the Payment queryset filtered by the logged-in company/user.
            """
            return (
                get_company_queryset(self.request, Payment)
                .select_related('company', 'branch', 'paid_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        Saves a new Payment instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"Payment '{payment.payment_number}' created by '{actor}' "
            f"for company '{payment.company.name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated Payment instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"Payment '{payment.payment_number}' updated by '{actor}' "
            f"for company '{payment.company.name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a Payment instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment_number = instance.payment_number
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"Payment '{payment_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )