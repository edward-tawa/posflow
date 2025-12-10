from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models import PaymentMethod
from payments.serializers.payment_method_serializer import PaymentMethodSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class PaymentMethodViewSet(ModelViewSet):
    """
    ViewSet for managing PaymentMethods.
    Supports listing, retrieving, creating, updating, and deleting methods.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'payment_method_name',
        'payment_method_code',
        'company__name',
        'branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'payment_method_name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, PaymentMethod).select_related('company', 'branch')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        method = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PaymentMethod '{method.payment_method_name}' created by '{actor}' for company '{method.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        method = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PaymentMethod '{method.payment_method_name}' updated by '{actor}' for company '{method.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        method_name = instance.payment_method_name
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PaymentMethod '{method_name}' deleted by '{actor}' from company '{company.name}'."
        )
