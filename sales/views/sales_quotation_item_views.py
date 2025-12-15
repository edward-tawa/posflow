from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_quotation_item_model import SalesQuotationItem
from sales.serializers.sales_quotation_item_serializer import SalesQuotationItemSerializer
from sales.services.sales_quotation_item_service import SalesQuotationItemService
from sales.models.sales_quotation_model import SalesQuotation
from sales.models.sales_invoice_model import SalesInvoice
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesQuotationItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Quotation Items.
    Supports listing, retrieving, creating, updating, and deleting quotation items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesQuotationItem.objects.all()
    serializer_class = SalesQuotationItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['product__name', 'sales_quotation__quotation_number', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesQuotationItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesQuotationItem)
                .select_related('sales_quotation', 'product', 'sales_quotation__company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesQuotationItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesQuotationItem for product '{item.product.name}' created by '{actor}' "
            f"for company '{item.sales_quotation.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesQuotationItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesQuotationItem for product '{item.product.name}' updated by '{actor}' "
            f"for company '{item.company.name}'."
        )



    @action(detail=True, methods=['post'], url_path='attach-quotation')
    def attach_quotation(self, request, pk=None):
        item = self.get_object()
        quotation_id = request.data.get("quotation_id")
        if not quotation_id:
            return Response({"detail": "quotation_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quotation = SalesQuotation.objects.get(id=quotation_id)
            updated_item = SalesQuotationItemService.attach_to_sales_quotation(item, quotation)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except SalesQuotation.DoesNotExist:
            return Response({"detail": "Quotation not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching quotation: {str(e)}")
            return Response({"detail": "Error attaching quotation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_path='attach-invoice')
    def attach_invoice(self, request, pk=None):
        item = self.get_object()
        invoice_id = request.data.get("invoice_id")
        if not invoice_id:
            return Response({"detail": "invoice_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            invoice = SalesInvoice.objects.get(id=invoice_id)
            updated_item = SalesQuotationItemService.attach_to_sales_invoice(item, invoice)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except SalesInvoice.DoesNotExist:
            return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching invoice: {str(e)}")
            return Response({"detail": "Error attaching invoice."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_path='detach-invoice')
    def detach_invoice(self, request, pk=None):
        item = self.get_object()
        try:
            updated_item = SalesQuotationItemService.detach_from_sales_invoice(item)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error detaching invoice: {str(e)}")
            return Response({"detail": "Error detaching invoice."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
