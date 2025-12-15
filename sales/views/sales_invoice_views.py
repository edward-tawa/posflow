from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_invoice_model import SalesInvoice
from sales.serializers.sales_invoice_serializer import SalesInvoiceSerializer
from sales.services.sales_invoice_service import SalesInvoiceService
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesInvoiceViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Invoices.
    Supports listing, retrieving, creating, updating, and deleting sales invoices.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesInvoice.objects.all()
    serializer_class = SalesInvoiceSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'invoice_number',
        'customer__name',
        'company__name',
        'branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'invoice_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesInvoice queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesInvoice)
                .select_related('company', 'branch', 'customer', 'issued_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesInvoice instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesInvoice '{invoice.invoice_number}' created by '{actor}' "
            f"for company '{invoice.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesInvoice instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesInvoice '{invoice.invoice_number}' updated by '{actor}' "
            f"for company '{invoice.company.name}'."
        )


    @action(detail=True, methods=['post'], url_path='apply-discount')
    def apply_discount(self, request, pk=None):
        try:
            invoice = self.get_object()
            discount_amount = float(request.data.get('discount_amount', 0))
            updated_invoice = SalesInvoiceService.apply_discount(invoice, discount_amount)
            serializer = self.get_serializer(updated_invoice)
            user = request.user
            company = get_logged_in_company(request)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.info(f"Applied discount of {discount_amount} to invoice '{invoice.invoice_number}' by '{actor}'.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error applying discount: {e}")
            return Response({"detail": "Error applying discount."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='void')
    def void_invoice(self, request, pk=None):
        try:
            invoice = self.get_object()
            reason = request.data.get('reason', '')
            updated_invoice = SalesInvoiceService.void_invoice(invoice, reason)
            serializer = self.get_serializer(updated_invoice)
            user = request.user
            company = get_logged_in_company(request)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.warning(f"Invoice '{invoice.invoice_number}' voided by '{actor}'. Reason: {reason}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error voiding invoice: {e}")
            return Response({"detail": "Error voiding invoice."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='mark-as-issued')
    def mark_as_issued(self, request, pk=None):
        try:
            invoice = self.get_object()
            updated_invoice = SalesInvoiceService.mark_as_issued(invoice)
            serializer = self.get_serializer(updated_invoice)
            user = request.user
            company = get_logged_in_company(request)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.info(f"Invoice '{invoice.invoice_number}' marked as ISSUED by '{actor}'.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error marking invoice as issued: {e}")
            return Response({"detail": "Error marking invoice as issued."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
