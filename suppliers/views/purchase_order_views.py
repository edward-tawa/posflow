from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from company.models.company_model import Company
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.serializers.purcahse_order_serializer import PurchaseOrderSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from loguru import logger



class PurchaseOrderViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Orders.
    Supports listing, retrieving, creating, updating, and deleting purchase orders.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['order_number', 'supplier__name', 'status']
    ordering_fields = ['order_date', 'created_at', 'updated_at']
    ordering = ['-order_date']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return PurchaseOrder queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, PurchaseOrder).select_related('supplier', 'company')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)
        logger.info(self.request.data)
        purchase_order = serializer.save(company=company)

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"PurchaseOrder '{purchase_order.reference_number}' created by '{actor}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_order = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseOrder '{purchase_order.order_number}' updated by '{actor}'."
        )


