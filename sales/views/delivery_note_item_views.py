from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.delivery_note_item_model import DeliveryNoteItem
from sales.serializers.delivery_note_item_serializer import DeliveryNoteItemSerializer
from loguru import logger


class DeliveryNoteItemViewSet(ModelViewSet):
    """
    ViewSet for managing DeliveryNoteItems.
    Supports listing, retrieving, creating, updating, and deleting delivery note items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = DeliveryNoteItem.objects.all()
    serializer_class = DeliveryNoteItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'delivery_note__delivery_number',
        'product__name',
        'product_name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the DeliveryNoteItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, DeliveryNoteItem)
                .select_related('delivery_note', 'delivery_note__company', 'product')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new DeliveryNoteItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        logger.success(
            f"DeliveryNoteItem for product '{item.product.name}' created for delivery note '{item.delivery_note.delivery_number}' by '{actor}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated DeliveryNoteItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        logger.info(
            f"DeliveryNoteItem for product '{item.product.name}' in delivery note '{item.delivery_note.delivery_number}' updated by '{actor}'."
        )
