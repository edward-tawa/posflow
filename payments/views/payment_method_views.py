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
from payments.services.payment_method_service import PaymentMethodService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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



    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        method = self.get_object()
        PaymentMethodService.activate_payment_method(method)
        return Response({"is_active": True}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        method = self.get_object()
        PaymentMethodService.deactivate_payment_method(method)
        return Response({"is_active": False}, status=status.HTTP_200_OK)

    # -------------------------
    # CRUD ACTIONS
    # -------------------------
    # Standard create, update, delete are handled by ModelViewSet,
    # but you could add soft-delete or special validation if needed.

    @action(detail=True, methods=['post'], url_path='delete')
    def delete_method(self, request, pk=None):
        method = self.get_object()
        PaymentMethodService.delete_payment_method(method)
        return Response({"deleted": True}, status=status.HTTP_200_OK)
