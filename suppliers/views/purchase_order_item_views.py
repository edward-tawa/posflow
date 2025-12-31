from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from suppliers.models.purchase_order_item_model import PurchaseOrderItem
from suppliers.serializers.purchase_order_item_serializer import PurchaseOrderItemSerializer
from suppliers.services.purchase_order_item_service import PurchaseOrderItemService
from suppliers.permissions.supplier_permissions import SupplierPermissions
from suppliers.permissions.supplier_product_permissions import SupplierProductPermissions
from suppliers.models.purchase_order_model import PurchaseOrder
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger



class PurchaseOrderItemViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Order Items.
    Supports listing, retrieving, creating, updating, and deleting purchase order items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierProductPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_order__order_number', 'product__name', 'status']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the PurchaseOrderItem queryset filtered by the logged-in company/user.
            -------------------
            """
            """Return PurchaseOrderItem queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, PurchaseOrderItem).select_related('purchase_order', 'product')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a new PurchaseOrderItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_order_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PurchaseOrderItem for product '{purchase_order_item.product.name}' created by '{actor}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates an existing PurchaseOrderItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_order_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseOrderItem for product '{purchase_order_item.product.name}' updated by '{actor}'."
        )


    @action(detail=True, methods=['post'], url_path='attach-to-order')
    def attach_to_order(self, request, pk=None):
        item = self.get_object()
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = PurchaseOrder.objects.get(id=order_id)
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "PurchaseOrder not found"}, status=status.HTTP_404_NOT_FOUND)

        item = PurchaseOrderItemService.attach_to_order(item, order)
        return Response(self.get_serializer(item).data, status=status.HTTP_200_OK)

    # -------------------------
    # DETACH ITEM FROM ORDER
    # -------------------------
    @action(detail=True, methods=['post'], url_path='detach-from-order')
    def detach_from_order(self, request, pk=None):
        item = self.get_object()
        item = PurchaseOrderItemService.detach_from_order(item)
        return Response(self.get_serializer(item).data, status=status.HTTP_200_OK)

    # -------------------------
    # UPDATE ITEM STATUS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        item = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "status is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = PurchaseOrderItemService.update_item_status(item, new_status)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(item).data, status=status.HTTP_200_OK)