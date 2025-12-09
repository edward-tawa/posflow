from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_queryset import get_company_queryset
from config.pagination.pagination import StandardResultsSetPagination
from suppliers.models.supplier_debit_note_item_model import SupplierDebitNoteItem
from suppliers.serializers.supplier_debit_note_item_serializer import SupplierDebitNoteItemSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from loguru import logger


class SupplierDebitNoteItemViewSet(ModelViewSet):
    """
    ViewSet for managing SupplierDebitNoteItems.
    Supports listing, retrieving, creating, updating, and deleting debit note items.
    Includes filtering, searching, ordering, company validation, and detailed logging.
    """

    queryset = SupplierDebitNoteItem.objects.all()
    serializer_class = SupplierDebitNoteItemSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['supplier_debit_note__debit_note_number', 'description']
    ordering_fields = ['quantity', 'unit_price', 'total_price', 'created_at', 'updated_at']
    ordering = ['-created_at']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return debit note items belonging to the logged-in user's company."""
            return (
                get_company_queryset(self.request, SupplierDebitNoteItem)
                .select_related('supplier_debit_note', 'supplier_debit_note__supplier', 'supplier_debit_note__company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """Create SupplierDebitNoteItem with company and logging enforcement."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        # Save item with company enforced through the debit note
        item = serializer.save()
        debit_note = item.supplier_debit_note
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SupplierDebitNoteItem '{item.id}' for debit note '{debit_note.debit_note_number}' "
            f"created by {actor}."
        )

    def perform_update(self, serializer):
        """Update SupplierDebitNoteItem with logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        item = serializer.save()
        debit_note = item.supplier_debit_note
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SupplierDebitNoteItem '{item.id}' for debit note '{debit_note.debit_note_number}' "
            f"updated by {actor}."
        )
