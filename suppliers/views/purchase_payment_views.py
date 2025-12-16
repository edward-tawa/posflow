from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from rest_framework.response import Response
from rest_framework import status
from suppliers.models.purchase_payment_model import PurchasePayment
from suppliers.serializers.purchase_payment_serializer import PurchasePaymentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PurchasePaymentViewSet(ModelViewSet):
    """
    ViewSet for managing PurchasePayments.
    Includes company scoping and detailed logging.
    """
    queryset = PurchasePayment.objects.all()
    serializer_class = PurchasePaymentSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_payment_number', 'supplier__name', 'branch__name']
    ordering_fields = ['created_at', 'updated_at', 'total_amount', 'payment_date']
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
                return PurchasePayment.objects.none()

            logger.info(f"{self._get_actor()} fetching PurchasePayments for company '{getattr(company, 'name', 'Unknown')}'.")
            return PurchasePayment.objects.filter(supplier__company=company)
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    # ---------------- Create ----------------
    def perform_create(self, serializer):
        company = self._get_company()
        serializer.validated_data['company'] = company  # enforce company
        payment = serializer.save()
        logger.bind(
            payment_number=getattr(payment, 'purchase_payment_number', 'Unknown'),
            supplier=getattr(payment.supplier, 'name', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"PurchasePayment '{payment.payment.payment_number}' for supplier '{payment.supplier}' created by {self._get_actor()} in company '{company.name}'."
        )

    # ---------------- Update ----------------
    def perform_update(self, serializer):
        payment = serializer.save()
        logger.bind(
            payment_number=getattr(payment, 'purchase_payment_number', 'Unknown'),
            supplier=getattr(payment.supplier, 'name', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"PurchasePayment '{payment.purchase_payment_number}' updated by {self._get_actor()}."
        )

    # ---------------- Destroy ----------------
    def perform_destroy(self, instance):
        logger.bind(
            payment_number=getattr(instance, 'purchase_payment_number', 'Unknown'),
            supplier=getattr(instance.supplier, 'name', 'Unknown'),
            actor=self._get_actor()
        ).warning(
            f"PurchasePayment '{instance.purchase_payment_number}' deleted by {self._get_actor()}."
        )
        instance.delete()

    


    # ---------------- Custom Actions ----------------
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        payment = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'status is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            PurchasePaymentService.update_payment_status(payment, new_status)
            return Response({'detail': f"Payment '{payment.id}' status updated to '{new_status}'."})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='attach-supplier')
    def attach_supplier(self, request, pk=None):
        payment = self.get_object()
        supplier_id = request.data.get('supplier_id')
        if not supplier_id:
            return Response({'detail': 'supplier_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        supplier = Supplier.objects.filter(id=supplier_id).first()
        if not supplier:
            return Response({'detail': 'Supplier not found.'}, status=status.HTTP_404_NOT_FOUND)
        PurchasePaymentService.attach_to_supplier(payment, supplier)
        return Response({'detail': f"Payment '{payment.id}' attached to supplier '{supplier.name}'."})

    @action(detail=True, methods=['post'], url_path='detach-supplier')
    def detach_supplier(self, request, pk=None):
        payment = self.get_object()
        PurchasePaymentService.detach_from_supplier(payment)
        return Response({'detail': f"Payment '{payment.id}' detached from its supplier."})

    @action(detail=True, methods=['post'], url_path='update-notes')
    def update_notes(self, request, pk=None):
        payment = self.get_object()
        new_notes = request.data.get('notes', '')
        PurchasePaymentService.update_payment_notes(payment, new_notes)
        return Response({'detail': f"Payment '{payment.id}' notes updated."})
