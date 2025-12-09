from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_queryset import get_company_queryset
from config.utilities.pagination import StandardResultsSetPagination
from suppliers.models.supplier_debit_note_model import SupplierDebitNote
from suppliers.serializers.supplier_debit_note_serializer import SupplierDebitNoteSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from loguru import logger


class SupplierDebitNoteViewSet(ModelViewSet):
    """
    ViewSet for managing SupplierDebitNotes.
    Supports listing, retrieving, creating, updating, and deleting debit notes.
    Includes filtering, searching, ordering, company validation, and detailed logging.
    """

    queryset = SupplierDebitNote.objects.all()
    serializer_class = SupplierDebitNoteSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['debit_note_number', 'supplier__name']
    ordering_fields = ['debit_date', 'total_amount', 'created_at', 'updated_at']
    ordering = ['-debit_date']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return debit notes belonging to the logged-in user's company."""
            return (
                get_company_queryset(self.request, SupplierDebitNote)
                .select_related('supplier', 'company', 'issued_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """Create SupplierDebitNote with company and logging enforcement."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        # Save debit note with company auto-bound
        debit_note = serializer.save(company=company)

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        supplier = debit_note.supplier

        logger.success(
            f"SupplierDebitNote '{debit_note.debit_note_number}' for supplier '{supplier.name}' "
            f"created in company '{company.name if company else None}' by {actor}."
        )

    def perform_update(self, serializer):
        """Update SupplierDebitNote with company validation and logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        debit_note = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        supplier = debit_note.supplier

        logger.info(
            f"SupplierDebitNote '{debit_note.debit_note_number}' for supplier '{supplier.name}' "
            f"updated by {actor}."
        )
