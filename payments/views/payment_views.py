from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models import Payment
from payments.serializers.payment_serializer import PaymentSerializer
from payments.services.payment_service import PaymentService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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



    @action(detail=True, methods=['post'], url_path='complete')
    def complete_payment(self, request, pk=None):
        payment = self.get_object()
        PaymentService.mark_payment_as_completed(payment)
        return Response({"status": "COMPLETED"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='fail')
    def fail_payment(self, request, pk=None):
        payment = self.get_object()
        PaymentService.mark_payment_as_failed(payment)
        return Response({"status": "FAILED"}, status=status.HTTP_200_OK)

    # -------------------------
    # RELATION ACTIONS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='attach-order')
    def attach_order(self, request, pk=None):
        payment = self.get_object()
        order_id = request.data.get("order_id")
        PaymentService.attach_payment_to_order(payment, order_id)
        return Response({"order_id": order_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-order')
    def detach_order(self, request, pk=None):
        payment = self.get_object()
        PaymentService.detach_payment_from_order(payment)
        return Response({"order_detached": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='attach-customer')
    def attach_customer(self, request, pk=None):
        payment = self.get_object()
        customer_id = request.data.get("customer_id")
        PaymentService.attach_payment_to_customer(payment, customer_id)
        return Response({"customer_id": customer_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-customer')
    def detach_customer(self, request, pk=None):
        payment = self.get_object()
        PaymentService.detach_payment_from_customer(payment)
        return Response({"customer_detached": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='attach-invoice')
    def attach_invoice(self, request, pk=None):
        payment = self.get_object()
        invoice_id = request.data.get("invoice_id")
        PaymentService.attach_payment_to_invoice(payment, invoice_id)
        return Response({"invoice_id": invoice_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-invoice')
    def detach_invoice(self, request, pk=None):
        payment = self.get_object()
        PaymentService.detach_payment_from_invoice(payment)
        return Response({"invoice_detached": True}, status=status.HTTP_200_OK)
