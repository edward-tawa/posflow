from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from suppliers.models.purchase_payment_allocation_model import PurchasePaymentAllocation
from suppliers.serializers.purchase_payment_allocation_serializer import PurchasePaymentAllocationSerializer
from loguru import logger


class PurchasePaymentAllocationViewSet(ModelViewSet):
    """
    ViewSet for managing PurchasePaymentAllocations.
    Company-scoped, with detailed logging for create, update, and delete.
    """
    queryset = PurchasePaymentAllocation.objects.all()
    serializer_class = PurchasePaymentAllocationSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'allocation_number',
        'supplier__name',
        'purchase_payment__purchase_payment_number',
        'purchase_invoice__invoice_number'
    ]
    ordering_fields = ['created_at', 'updated_at', 'allocated_amount', 'allocation_date']
    ordering = ['-created_at']

    # ---------------- Helper Methods ----------------
    def _get_company(self):
        """Returns the company context for the request."""
        user = self.request.user
        return getattr(user, 'company', None) or get_expected_company(self.request)

    def _get_actor(self):
        """Returns a string identifying who is performing the action."""
        user = self.request.user
        company = self._get_company()
        return getattr(user, 'username', None) or getattr(company, 'name', None) or 'Unknown'

    # ---------------- QuerySet ----------------
    def get_queryset(self):
        company = self._get_company()
        if not company:
            logger.warning(f"{self._get_actor()} has no associated company context.")
            return PurchasePaymentAllocation.objects.none()

        logger.info(f"{self._get_actor()} fetching PurchasePaymentAllocations for company '{getattr(company, 'name', 'Unknown')}'.")
        return PurchasePaymentAllocation.objects.filter(company=company)

    # ---------------- Create ----------------
    def perform_create(self, serializer):
        company = self._get_company()
        serializer.validated_data['company'] = company  # enforce company
        allocation = serializer.save()
        logger.bind(
            allocation_number=getattr(allocation, 'allocation_number', 'Unknown'),
            supplier=getattr(allocation.supplier, 'name', 'Unknown'),
            invoice=getattr(allocation.purchase_invoice, 'invoice_number', 'Unknown'),
            payment=getattr(allocation.purchase_payment, 'purchase_payment_number', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"PurchasePaymentAllocation '{allocation.allocation_number}' of amount '{allocation.allocated_amount}' "
            f"applied to invoice '{allocation.purchase_invoice.invoice_number}' from payment "
            f"'{allocation.purchase_payment.payment.payment_number}' for supplier '{allocation.supplier.name}' "
            f"by '{self._get_actor()}'."
        )

    # ---------------- Update ----------------
    def perform_update(self, serializer):
        allocation = serializer.save()
        logger.bind(
            allocation_number=getattr(allocation, 'allocation_number', 'Unknown'),
            supplier=getattr(allocation.supplier, 'name', 'Unknown'),
            invoice=getattr(allocation.purchase_invoice, 'invoice_number', 'Unknown'),
            payment=getattr(allocation.purchase_payment, 'purchase_payment_number', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"PurchasePaymentAllocation '{allocation.allocation_number}' updated by '{self._get_actor()}'."
        )

    # ---------------- Destroy ----------------
    def perform_destroy(self, instance):
        logger.bind(
            allocation_number=getattr(instance, 'allocation_number', 'Unknown'),
            supplier=getattr(instance.supplier, 'name', 'Unknown'),
            invoice=getattr(instance.purchase_invoice, 'invoice_number', 'Unknown'),
            payment=getattr(instance.purchase_payment, 'purchase_payment_number', 'Unknown'),
            actor=self._get_actor()
        ).warning(
            f"PurchasePaymentAllocation '{instance.allocation_number}' deleted by '{self._get_actor()}'."
        )
        instance.delete()
