from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_quotation_model import SalesQuotation
from sales.serializers.sales_quotation_serializer import SalesQuotationSerializer
from sales.services.sales_quotation_service import SalesQuotationService
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesQuotationViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Quotations.
    Supports listing, retrieving, creating, updating, and deleting quotations.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesQuotation.objects.all()
    serializer_class = SalesQuotationSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['quotation_number', 'customer__name', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'quotation_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesQuotation queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesQuotation)
                .select_related('company', 'branch', 'customer', 'created_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesQuotation instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        quotation = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesQuotation '{quotation.quotation_number}' created by '{actor}' "
            f"for company '{quotation.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesQuotation instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        quotation = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesQuotation '{quotation.quotation_number}' updated by '{actor}' "
            f"for company '{quotation.company.name}'."
        )


    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        quotation = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_quotation = SalesQuotationService.update_sales_quotation_status(quotation, new_status)
            serializer = self.get_serializer(updated_quotation)
            return Response(serializer.data)
        except ValueError as ve:
            return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            return Response({"detail": "Error updating status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    @action(detail=True, methods=['post'], url_path='attach-customer')
    def attach_customer(self, request, pk=None):
        quotation = self.get_object()
        customer_id = request.data.get("customer_id")
        if not customer_id:
            return Response({"detail": "customer_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from customers.models.customer_model import Customer
            customer = Customer.objects.get(id=customer_id)
            updated_quotation = SalesQuotationService.attach_to_customer(quotation, customer)
            serializer = self.get_serializer(updated_quotation)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching customer: {str(e)}")
            return Response({"detail": "Error attaching customer."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='detach-customer')
    def detach_customer(self, request, pk=None):
        quotation = self.get_object()
        try:
            updated_quotation = SalesQuotationService.detach_from_customer(quotation)
            serializer = self.get_serializer(updated_quotation)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error detaching customer: {str(e)}")
            return Response({"detail": "Error detaching customer."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)