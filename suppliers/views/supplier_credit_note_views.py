from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from suppliers.models.supplier_credit_note_model import SupplierCreditNote
from suppliers.serializers.supplier_credit_note_serializer import SupplierCreditNoteSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
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
                return SupplierCreditNote.objects.none()

            logger.info(f"{self._get_actor()} fetching SupplierCreditNotes for company '{getattr(company, 'name', 'Unknown')}'.")
            return SupplierCreditNote.objects.filter(company=company)
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

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



    # ---------------- Custom Actions ----------------
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        credit_note = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'status is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            SupplierCreditNoteService.update_supplier_credit_note_status(credit_note, new_status)
            return Response({'detail': f"Credit note '{credit_note.id}' status updated to '{new_status}'."})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='attach-supplier')
    def attach_supplier(self, request, pk=None):
        credit_note = self.get_object()
        supplier_id = request.data.get('supplier_id')
        if not supplier_id:
            return Response({'detail': 'supplier_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        supplier = Supplier.objects.filter(id=supplier_id).first()
        if not supplier:
            return Response({'detail': 'Supplier not found.'}, status=status.HTTP_404_NOT_FOUND)
        SupplierCreditNoteService.attach_to_supplier(credit_note, supplier)
        return Response({'detail': f"Credit note '{credit_note.id}' attached to supplier '{supplier.id}'."})

    @action(detail=True, methods=['post'], url_path='detach-supplier')
    def detach_supplier(self, request, pk=None):
        credit_note = self.get_object()
        SupplierCreditNoteService.detach_from_supplier(credit_note)
        return Response({'detail': f"Credit note '{credit_note.id}' detached from supplier."})
