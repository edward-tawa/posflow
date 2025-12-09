from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from rest_framework.response import Response
from rest_framework import status
from suppliers.models.purchase_payment_model import PurchasePayment
from suppliers.serializers.purchase_payment_serializer import PurchasePaymentSerializer
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
            return f"Error: {e}"

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
