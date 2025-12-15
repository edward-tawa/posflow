from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sale_model import Sale
from sales.serializers.sale_serializer import SaleSerializer
from sales.services.sale_service import SaleService
from sales.models.sales_receipt_model import SalesReceipt
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesViewSet(ModelViewSet):
    """
    ViewSet for managing Sales.
    Supports listing, retrieving, creating, updating, and deleting sales.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'sale_number',
        'customer__name',
        'branch__name',
        'company__name',
        'issued_by__username'
    ]
    ordering_fields = ['created_at', 'updated_at', 'sales_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the Sales queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, Sale)
                .select_related('company', 'branch', 'customer', 'issued_by', 'sales_invoice', 'sales_receipt')
            )
        except Exception as e:
            logger.error(f"Error fetching Sales queryset: {e}")
            return Sale.objects.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new Sales instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sale = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"Sale '{sale.sale_number}' created by '{actor}' "
            f"for company '{sale.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated Sales instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sale = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"Sale '{sale.sale_number}' updated by '{actor}' "
            f"for company '{sale.company.name}'."
        )

    @action(detail=False, methods=['get'], url_path='by-customer/(?P<customer_id>[^/.]+)')
    def get_sales_by_customer(self, request, customer_id=None):
        try:
            sales = SaleService.get_sales_by_customer(customer_id)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(sales, request)
            serializer = self.get_serializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving sales for customer {customer_id}: {e}")
            return Response({"detail": "Error retrieving sales."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='by-branch/(?P<branch_id>[^/.]+)')
    def get_sales_by_branch(self, request, branch_id=None):
        try:
            sales = SaleService.get_sales_by_branch(branch_id)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(sales, request)
            serializer = self.get_serializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving sales for branch {branch_id}: {e}")
            return Response({"detail": "Error retrieving sales."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post', 'patch'], url_path='cancel')
    def cancel_sale(self, request, pk=None):
        try:
            sale = self.get_object()
            SaleService.cancel_sale(sale)  # Use service layer

            user = request.user
            company = get_logged_in_company(request)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

            logger.warning(f"Sale '{sale.sale_number}' cancelled by '{actor}' for company '{sale.company.name}'.")

            serializer = self.get_serializer(sale)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error cancelling sale {pk}: {e}")
            return Response({"detail": "Error cancelling sale."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post', 'patch'], url_path='mark-as-paid')
    def mark_as_paid(self, request, pk=None):
        try:
            sale = self.get_object()
            receipt_id = request.data.get('receipt_id')
            receipt = None
            if receipt_id:
                receipt = SalesReceipt.objects.get(id=receipt_id)

            SaleService.mark_as_paid(sale, receipt)  # Use service layer

            user = request.user
            company = get_logged_in_company(request)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.info(f"Sale '{sale.sale_number}' marked as fully paid by '{actor}'.")

            serializer = self.get_serializer(sale)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except SalesReceipt.DoesNotExist:
            return Response({"detail": "Receipt not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error marking sale {sale.sale_number} as paid: {str(e)}")
            return Response({"detail": "Error marking sale as paid."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    