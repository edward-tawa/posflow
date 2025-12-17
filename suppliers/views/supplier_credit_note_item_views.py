from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_queryset import get_company_queryset
from config.pagination.pagination import StandardResultsSetPagination
from suppliers.models.supplier_credit_note_item_model import SupplierCreditNoteItem
from suppliers.serializers.supplier_credit_note_item_serializer import SupplierCreditNoteItemSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from suppliers.permissions.supplier_credit_note_permissions import SupplierCreditNotePermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class SupplierCreditNoteItemViewSet(ModelViewSet):
    """
    ViewSet for managing SupplierCreditNoteItems.
    Supports listing, retrieving, creating, updating, and deleting items.
    Includes filtering, searching, ordering, company validation, and detailed logging.
    """

    queryset = SupplierCreditNoteItem.objects.all()
    serializer_class = SupplierCreditNoteItemSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SupplierCreditNoteItem]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['supplier_credit_note__credit_note_number', 'description']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price', 'total_price']
    ordering = ['-created_at']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return items belonging to the logged-in user's company."""
            return (
                get_company_queryset(self.request, SupplierCreditNoteItem)
                .select_related('supplier_credit_note', 'supplier_credit_note__supplier', 'supplier_credit_note__company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """Create SupplierCreditNoteItem with company and logging enforcement."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        # Save item with company auto-bound via the related credit note
        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        note = item.supplier_credit_note

        logger.success(
            f"SupplierCreditNoteItem {item.id} for credit note '{note.credit_note_number}' "
            f"created by {actor}."
        )

    def perform_update(self, serializer):
        """Update SupplierCreditNoteItem with logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        item = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        note = item.supplier_credit_note

        logger.info(
            f"SupplierCreditNoteItem {item.id} for credit note '{note.credit_note_number}' "
            f"updated by {actor}."
        )



    @action(detail=True, methods=['post'], url_path='attach-credit-note')
    def attach_credit_note(self, request, pk=None):
        item = self.get_object()
        credit_note_id = request.data.get('credit_note_id')
        if not credit_note_id:
            return Response({'detail': 'credit_note_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        credit_note = SupplierCreditNote.objects.filter(id=credit_note_id).first()
        if not credit_note:
            return Response({'detail': 'Credit note not found.'}, status=status.HTTP_404_NOT_FOUND)
        SupplierCreditNoteItemService.attach_to_credit_note(item, credit_note)
        return Response({'detail': f"Credit note item '{item.id}' attached to credit note '{credit_note.id}'."})

    @action(detail=True, methods=['post'], url_path='detach-credit-note')
    def detach_credit_note(self, request, pk=None):
        item = self.get_object()
        SupplierCreditNoteItemService.detach_from_credit_note(item)
        return Response({'detail': f"Credit note item '{item.id}' detached from credit note."})

    @action(detail=True, methods=['post'], url_path='update-quantity')
    def update_quantity(self, request, pk=None):
        item = self.get_object()
        new_quantity = request.data.get('quantity')
        if new_quantity is None:
            return Response({'detail': 'quantity is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            SupplierCreditNoteItemService.update_supplier_credit_note_item_quantity(item, int(new_quantity))
            return Response({'detail': f"Credit note item '{item.id}' quantity updated to {new_quantity}."})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-unit-price')
    def update_unit_price(self, request, pk=None):
        item = self.get_object()
        new_price = request.data.get('unit_price')
        if new_price is None:
            return Response({'detail': 'unit_price is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            SupplierCreditNoteItemService.update_supplier_credit_note_item_unit_price(item, float(new_price))
            return Response({'detail': f"Credit note item '{item.id}' unit price updated to {new_price}."})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)