from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_queryset import get_company_queryset
from config.pagination.pagination import StandardResultsSetPagination
from suppliers.models.supplier_debit_note_item_model import SupplierDebitNoteItem
from suppliers.models.supplier_debit_note_model import SupplierDebitNote
from suppliers.serializers.supplier_debit_note_item_serializer import SupplierDebitNoteItemSerializer
from suppliers.services.supplier_debit_note_item_service import SupplierDebitNoteItemService
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
        """Return debit note items belonging to the logged-in user's company."""
        try:
            return (
                get_company_queryset(self.request, SupplierDebitNoteItem)
                .select_related('supplier_debit_note', 'supplier_debit_note__supplier', 'supplier_debit_note__company')
            )
        except Exception as e:
            logger.error(f"Error fetching SupplierDebitNoteItems: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """Create SupplierDebitNoteItem with company and logging enforcement."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        # Save item using service (optional, if you want validation and business rules enforced)
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

    def perform_destroy(self, instance):
        """Delete SupplierDebitNoteItem with logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        debit_note = instance.supplier_debit_note
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"SupplierDebitNoteItem '{instance.id}' for debit note '{debit_note.debit_note_number}' "
            f"deleted by {actor}."
        )
        instance.delete()

    # -------------------------
    # Optional Action Methods
    # -------------------------
    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Custom action to update status of a debit note item if needed."""
        item = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Example: using a service method for business rules
        try:
            SupplierDebitNoteItemService.update_item_status(item, new_status)
            return Response({"detail": f"SupplierDebitNoteItem '{item.id}' status updated to '{new_status}'."})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
