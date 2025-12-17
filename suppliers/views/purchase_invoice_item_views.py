from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from rest_framework.response import Response
from rest_framework import status
from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem
from suppliers.serializers.purchase_invoice_item_serializer import PurchaseInvoiceItemSerializer
from suppliers.permissions.supplier_product_permissions import SupplierProductPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PurchaseInvoiceItemViewSet(ModelViewSet):
    """
    ViewSet for managing PurchaseInvoiceItems.
    Includes company scoping and detailed logging.
    """
    queryset = PurchaseInvoiceItem.objects.all()
    serializer_class = PurchaseInvoiceItemSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierProductPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_invoice__invoice_number', 'product__name']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price', 'total_price']
    ordering = ['-created_at']

    # ---------------- Helper Methods ----------------
    def _get_company(self):
        try:
            """Returns the company context for the request."""
            user = self.request.user
            return getattr(user, 'company', None) or get_expected_company(self.request)
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def _get_actor(self):
        try:
            """Returns a string identifying who is performing the action."""
            user = self.request.user
            company = self._get_company()
            return getattr(user, 'username', None) or getattr(company, 'name', None) or 'Unknown'
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    # ---------------- QuerySet ----------------
    def get_queryset(self):
        try:
            company = self._get_company()
            if not company:
                logger.warning(f"{self._get_actor()} has no associated company context.")
                return PurchaseInvoiceItem.objects.none()

            logger.info(f"{self._get_actor()} fetching PurchaseInvoiceItems for company '{getattr(company, 'name', 'Unknown')}'.")
            return PurchaseInvoiceItem.objects.filter(purchase_invoice__company=company)
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    # ---------------- Create ----------------
    def perform_create(self, serializer):
        company = self._get_company()
        item = serializer.save()
        logger.bind(
            invoice=getattr(item.purchase_invoice, 'invoice_number', 'Unknown'),
            product=getattr(item.product, 'name', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"PurchaseInvoiceItem for product '{item.product.name}' added to invoice '{item.purchase_invoice.invoice_number}' by {self._get_actor()}."
        )

    # ---------------- Update ----------------
    def perform_update(self, serializer):
        item = serializer.save()
        logger.bind(
            invoice=getattr(item.purchase_invoice, 'invoice_number', 'Unknown'),
            product=getattr(item.product, 'name', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"PurchaseInvoiceItem {item.id} for product '{item.product.name}' updated by {self._get_actor()}."
        )

    # ---------------- Destroy ----------------
    def perform_destroy(self, instance):
        logger.bind(
            invoice=getattr(instance.purchase_invoice, 'invoice_number', 'Unknown'),
            product=getattr(instance.product, 'name', 'Unknown'),
            actor=self._get_actor()
        ).warning(
            f"PurchaseInvoiceItem {instance.id} for product '{instance.product.name}' deleted by {self._get_actor()}."
        )
        instance.delete()


    @action(detail=True, methods=['post'], url_path='attach-to-invoice')
    def attach_to_invoice(self, request, pk=None):
        item = self.get_object()
        invoice_id = request.data.get('invoice_id')
        if not invoice_id:
            return Response({"error": "invoice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = PurchaseInvoice.objects.get(id=invoice_id)
        except PurchaseInvoice.DoesNotExist:
            return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

        item = PurchaseInvoiceItemService.attach_to_invoice(item, invoice)
        return Response(self.get_serializer(item).data, status=status.HTTP_200_OK)

    # -------------------------
    # DETACH FROM INVOICE
    # -------------------------
    @action(detail=True, methods=['post'], url_path='detach-from-invoice')
    def detach_from_invoice(self, request, pk=None):
        item = self.get_object()
        item = PurchaseInvoiceItemService.detach_from_invoice(item)
        return Response(self.get_serializer(item).data, status=status.HTTP_200_OK)
