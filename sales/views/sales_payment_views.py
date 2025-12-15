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
from sales.services.sales_payment_service import SalesPaymentService
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
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




    @action(detail=False, methods=['post'], url_path='apply')
    def apply_payment(self, request):
        try:
            sales_order_id = request.data.get("sales_order")
            sales_receipt_id = request.data.get("sales_receipt")
            payment_id = request.data.get("payment")
            amount = request.data.get("amount")

            if not all([sales_order_id, sales_receipt_id, payment_id, amount]):
                return Response({"detail": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

            # You would typically fetch sales_order, sales_receipt, payment objects here
            sales_payment = SalesPaymentService.create_sales_payment(
                sales_order=request.data['sales_order'],
                sales_receipt=request.data['sales_receipt'],
                payment=request.data['payment'],
                amount=request.data['amount']
            )
            serializer = self.get_serializer(sales_payment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error applying payment: {e}")
            return Response({"detail": "Error applying payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='update-amount')
    def update_amount(self, request, pk=None):
        sales_payment = self.get_object()
        new_amount = request.data.get("new_amount")
        if new_amount is None:
            return Response({"detail": "new_amount is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_payment = SalesPaymentService.update_sales_payment(sales_payment, new_amount)
            serializer = self.get_serializer(updated_payment)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating payment amount: {e}")
            return Response({"detail": "Error updating payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'], url_path='reverse')
    def reverse_payment(self, request, pk=None):
        sales_payment = self.get_object()
        try:
            SalesPaymentService.delete_sales_payment(sales_payment)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error reversing payment: {e}")
            return Response({"detail": "Error reversing payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)