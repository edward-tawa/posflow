from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.delivery_note_model import DeliveryNote
from sales.serializers.delivery_note_serializer import DeliveryNoteSerializer
from loguru import logger


class DeliveryNoteViewSet(ModelViewSet):
    """
    ViewSet for managing DeliveryNotes.
    Supports listing, retrieving, creating, updating, and deleting delivery notes.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = DeliveryNote.objects.all()
    serializer_class = DeliveryNoteSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'delivery_number',
        'sales_order__order_number',
        'customer__name',
        'company__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'delivery_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns the DeliveryNote queryset filtered by the logged-in company/user.
        -------------------
        """
        return (
            get_company_queryset(self.request, DeliveryNote)
            .select_related('company', 'branch', 'customer', 'sales_order', 'issued_by')
        )

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new DeliveryNote instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        delivery_note = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"DeliveryNote '{delivery_note.delivery_number}' created by '{actor}' "
            f"for company '{delivery_note.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated DeliveryNote instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        delivery_note = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"DeliveryNote '{delivery_note.delivery_number}' updated by '{actor}' "
            f"for company '{delivery_note.company.name}'."
        )
