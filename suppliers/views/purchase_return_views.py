from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from suppliers.models.purchase_return_model import PurchaseReturn
from suppliers.services.purchase_return_service import PurchaseReturnService
from suppliers.serializers.purchase_return_serializer import PurchaseReturnSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from suppliers.models.supplier_model import Supplier
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PurchaseReturnViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Returns.
    Supports listing, retrieving, creating, updating, and deleting purchase returns.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchaseReturn.objects.all()
    serializer_class = PurchaseReturnSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_return_number', 'purchase_order__order_number', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'return_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the PurchaseReturn queryset filtered by the logged-in company/user.
            -------------------
            """
            return get_company_queryset(self.request, PurchaseReturn).select_related('company', 'purchase_order')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a new PurchaseReturn instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_return = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"PurchaseReturn '{purchase_return.purchase_return_number}' created by '{actor}' "
            f"for company '{purchase_return.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates an existing PurchaseReturn instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_return = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseReturn '{purchase_return.purchase_return_number}' updated by '{actor}' "
            f"for company '{purchase_return.company.name}'."
        )


    
    # ---------------- Custom Actions ----------------
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        purchase_return = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'status is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            PurchaseReturnService.update_purchase_return_status(purchase_return, new_status)
            return Response({'detail': f"Purchase Return '{purchase_return.id}' status updated to '{new_status}'."})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='attach-supplier')
    def attach_supplier(self, request, pk=None):
        purchase_return = self.get_object()
        supplier_id = request.data.get('supplier_id')
        if not supplier_id:
            return Response({'detail': 'supplier_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        supplier = Supplier.objects.filter(id=supplier_id).first()
        if not supplier:
            return Response({'detail': 'Supplier not found.'}, status=status.HTTP_404_NOT_FOUND)
        PurchaseReturnService.attach_to_supplier(purchase_return, supplier)
        return Response({'detail': f"Purchase Return '{purchase_return.id}' attached to supplier '{supplier.name}'."})

    @action(detail=True, methods=['post'], url_path='detach-supplier')
    def detach_supplier(self, request, pk=None):
        purchase_return = self.get_object()
        PurchaseReturnService.detach_from_supplier(purchase_return)
        return Response({'detail': f"Purchase Return '{purchase_return.id}' detached from supplier."})