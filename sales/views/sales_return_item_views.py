from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication
)
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_return_item_model import SalesReturnItem 
from sales.permissions.sales_product_permissions import SalesProductPermissions
from sales.serializers.sales_return_item_serializer import SalesReturnItemSerializer
from sales.services.sales_return_item_service import SalesReturnItemService
from sales.models.sales_return_model import SalesReturn
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesReturnItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Return Items.
    Supports listing, retrieving, creating, updating, and deleting items.
    Includes filtering, searching, ordering, and structured logging.
    """

    queryset = SalesReturnItem.objects.select_related(
        'sales_return',
        'product'
    )
    serializer_class = SalesReturnItemSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesProductPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'product__name',
        'sales_return__return_number',
        'sales_return__customer__first_name'
    ]
    ordering_fields = [
        'created_at',
        'updated_at',
        'quantity',
        'unit_price',
        'total_price'
    ]
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns items filtered by the logged-in company
            using the parent sales_return.company relationship.
            -------------------
            """
            return (
                get_company_queryset(
                    self.request,
                    SalesReturnItem,
                    # parent_field='sales_return__company'
                )
                .select_related('product')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a SalesReturnItem and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesReturnItem '{item.product.name}' added to SalesReturn '{item.sales_return.return_number}' "
            f"by '{actor}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates a SalesReturnItem and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesReturnItem '{item.product_name}' updated on SalesReturn '{item.sales_return.return_number}' "
            f"by '{actor}'."
        )



    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        item = self.get_object()
        new_status = request.data.get("new_status")
        if not new_status:
            return Response({"detail": "new_status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_item = SalesReturnItemService.update_sales_return_item_status(item, new_status)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating sales return item status: {str(e)}")
            return Response({"detail": "Error updating status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='attach-to-return')
    def attach_to_return(self, request, pk=None):
        item = self.get_object()
        sales_return_id = request.data.get("sales_return_id")
        if not sales_return_id:
            return Response({"detail": "sales_return_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sales_return = SalesReturn.objects.get(id=sales_return_id)
            updated_item = SalesReturnItemService.attach_to_sales_return(item, sales_return)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except SalesReturn.DoesNotExist:
            return Response({"detail": "SalesReturn not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching item to sales return: {str(e)}")
            return Response({"detail": "Error attaching item."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
