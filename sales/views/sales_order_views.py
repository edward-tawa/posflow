from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_order_model import SalesOrder
from sales.serializers.sales_order_serializer import SalesOrderSerializer
from sales.services.sales_order_service import SalesOrderService
from sales.serializers.sales_order_item_serializer import SalesOrderItemSerializer
from sales.models.sales_invoice_model import SalesInvoice
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger



class SalesOrderViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Orders.
    Supports listing, retrieving, creating, updating, and deleting sales orders.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'order_number',
        'customer__name',
        'branch__name',
        'company__name',
        'sales_person__username'
    ]
    ordering_fields = ['created_at', 'updated_at', 'order_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesOrder queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesOrder)
                .select_related('company', 'branch', 'customer', 'sales_person')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesOrder instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        order = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesOrder '{order.order_number}' created by '{actor}' "
            f"for company '{order.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesOrder instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        order = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesOrder '{order.order_number}' updated by '{actor}' "
            f"for company '{order.company.name}'."
        )
    


    @action(detail=True, methods=['post'], url_path='attach-invoice')
    def attach_invoice(self, request, pk=None):
        order = self.get_object()
        invoice_id = request.data.get("invoice_id")
        if not invoice_id:
            return Response({"detail": "invoice_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            invoice = SalesInvoice.objects.get(id=invoice_id)
            updated_order = SalesOrderService.attach_to_invoice(order, invoice)
            serializer = self.get_serializer(updated_order)
            return Response(serializer.data)
        except SalesInvoice.DoesNotExist:
            return Response({"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching invoice: {str(e)}")
            return Response({"detail": "Error attaching invoice."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_order = SalesOrderService.update_sales_order_status(order, new_status)
            serializer = self.get_serializer(updated_order)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            return Response({"detail": "Error updating status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='bulk-items')
    def bulk_items(self, request, pk=None):
        order = self.get_object()
        items_data = request.data.get("items_data", [])
        if not items_data:
            return Response({"detail": "items_data is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            created_items = SalesOrderService.bulk_create_order_items(order, items_data)
            # Assuming you have a serializer for order items
            serializer = SalesOrderItemSerializer(created_items, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error bulk creating order items: {str(e)}")
            return Response({"detail": "Error creating order items."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
