from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from suppliers.models.supplier_credit_note_model import SupplierCreditNote
from suppliers.serializers.supplier_credit_note_serializer import SupplierCreditNoteSerializer
from loguru import logger


class SupplierCreditNoteViewSet(ModelViewSet):
    """
    ViewSet for managing SupplierCreditNotes.
    Company-scoped, with detailed logging for create, update, and delete.
    """
    queryset = SupplierCreditNote.objects.all()
    serializer_class = SupplierCreditNoteSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['credit_note_number', 'supplier__name']
    ordering_fields = ['created_at', 'updated_at', 'total_amount', 'credit_date']
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
            return SupplierCreditNote.objects.none()

        logger.info(f"{self._get_actor()} fetching SupplierCreditNotes for company '{getattr(company, 'name', 'Unknown')}'.")
        return SupplierCreditNote.objects.filter(company=company)

    # ---------------- Create ----------------
    def perform_create(self, serializer):
        company = self._get_company()
        serializer.validated_data['company'] = company  # enforce company
        credit_note = serializer.save()
        logger.bind(
            credit_note_number=getattr(credit_note, 'credit_note_number', 'Unknown'),
            supplier=getattr(credit_note.supplier, 'name', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"SupplierCreditNote '{credit_note.credit_note_number}' for supplier '{credit_note.supplier.name}' "
            f"created by '{self._get_actor()}' in company '{company.name}'."
        )

    # ---------------- Update ----------------
    def perform_update(self, serializer):
        credit_note = serializer.save()
        logger.bind(
            credit_note_number=getattr(credit_note, 'credit_note_number', 'Unknown'),
            supplier=getattr(credit_note.supplier, 'name', 'Unknown'),
            actor=self._get_actor()
        ).info(
            f"SupplierCreditNote '{credit_note.credit_note_number}' updated by '{self._get_actor()}'."
        )

    # ---------------- Destroy ----------------
    def perform_destroy(self, instance):
        logger.bind(
            credit_note_number=getattr(instance, 'credit_note_number', 'Unknown'),
            supplier=getattr(instance.supplier, 'name', 'Unknown'),
            actor=self._get_actor()
        ).warning(
            f"SupplierCreditNote '{instance.credit_note_number}' deleted by '{self._get_actor()}'."
        )
        instance.delete()
