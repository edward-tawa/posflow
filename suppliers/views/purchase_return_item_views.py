from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_company_or_user_company import get_expected_company
from config.pagination.pagination import StandardResultsSetPagination
from suppliers.models.purchase_return_item_model import PurchaseReturnItem
from suppliers.serializers.purchase_return_item_serializer import PurchaseReturnItemSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PurchaseReturnItemViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Return Items.
    Supports listing, retrieving, creating, updating, and deleting purchase return items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchaseReturnItem.objects.all()
    serializer_class = PurchaseReturnItemSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_return__purchase_return_number', 'product__name']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the PurchaseReturnItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return get_company_queryset(self.request, PurchaseReturnItem).select_related('purchase_return', 'product')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a new PurchaseReturnItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_return_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', None)

        logger.success(
            f"PurchaseReturnItem for product '{purchase_return_item.product.name}' created by '{actor}' "
            f"under PurchaseReturn '{purchase_return_item.purchase_return.purchase_return_number}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates an existing PurchaseReturnItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_return_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseReturnItem for product '{purchase_return_item.product.name}' updated by '{actor}' "
            f"under PurchaseReturn '{purchase_return_item.purchase_return.purchase_return_number}'."
        )



    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        item = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'status is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            PurchaseReturnItemService.update_item_status(item, new_status)
            return Response({'detail': f"Item '{item.product_name}' status updated to '{new_status}'."})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='attach-return')
    def attach_return(self, request, pk=None):
        item = self.get_object()
        return_id = request.data.get('purchase_return_id')
        if not return_id:
            return Response({'detail': 'purchase_return_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        purchase_return = PurchaseReturn.objects.filter(id=return_id).first()
        if not purchase_return:
            return Response({'detail': 'PurchaseReturn not found.'}, status=status.HTTP_404_NOT_FOUND)
        PurchaseReturnItemService.attach_to_return(item, purchase_return)
        return Response({'detail': f"Item '{item.product_name}' attached to return '{purchase_return.id}'."})

    @action(detail=True, methods=['post'], url_path='detach-return')
    def detach_return(self, request, pk=None):
        item = self.get_object()
        PurchaseReturnItemService.detach_from_return(item)
        return Response({'detail': f"Item '{item.product_name}' detached from its return."})