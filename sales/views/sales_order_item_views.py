from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_product_permissions import SalesProductPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_order_item_model import SalesOrderItem
from sales.serializers.sales_order_item_serializer import SalesOrderItemSerializer
from sales.services.sales_order_item_service import SalesOrderItemService
from sales.models.sales_order_model import SalesOrder
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesOrderItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Order Items.
    Supports listing, retrieving, creating, updating, and deleting sales order items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesProductPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'product__name',
        'sales_order__order_number',
        'sales_order__customer_name',
        'sales_order__company__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesOrderItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesOrderItem)
                .select_related('product', 'sales_order', 'sales_order__company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesOrderItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesOrderItem '{item.product_name}' created by '{actor}' "
            f"for SalesOrder '{item.sales_order.order_number}' and company '{item.sales_order.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesOrderItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesOrderItem '{item.product_name}' updated by '{actor}' "
            f"for SalesOrder '{item.sales_order.order_number}' and company '{item.sales_order.company.name}'."
        )



    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        item = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_item = SalesOrderItemService.update_sales_order_item_status(item, new_status)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating item status: {str(e)}")
            return Response({"detail": "Error updating item status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='attach-order')
    def attach_order(self, request, pk=None):
        item = self.get_object()
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"detail": "order_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = SalesOrder.objects.get(id=order_id)
            updated_item = SalesOrderItemService.attach_to_sales_order(item, order)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except SalesOrder.DoesNotExist:
            return Response({"detail": "Sales Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching item to order: {str(e)}")
            return Response({"detail": "Error attaching item to order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
