from rest_framework.viewsets import ModelViewSet
from transfers.models.product_transfer_model import ProductTransfer
from transfers.serializers.product_transfer_serializer import ProductTransferSerializer
from config.permissions.company_role_base_permission import CompanyRolePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from transfers.django_filters.product_transfer_filters import ProductTransferFilter
from rest_framework import status
from rest_framework.response import Response
from company.models.company_model import Company
from config.pagination.pagination import StandardResultsSetPagination
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from rest_framework.decorators import action
from transfers.models.transfer_model import Transfer
from transfers.services.product_service.product_transfer_service import ProductTransferService, ProductTransferError
from loguru import logger


class ProductTransferViewSet(ModelViewSet):
    """
    ViewSet for managing Product Transfers within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = ProductTransfer.objects.all()
    serializer_class = ProductTransferSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]
    permission_classes = [CompanyRolePermission]
    
    # Correct filter setup
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductTransferFilter
    
    search_fields = ['transfer__reference_number', 'transfer__transfer_date', 'source_branch__name', 'destination_branch__name', 'transfer__status']
    ordering_fields = ['transfer__transfer_date', 'created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, ProductTransfer).select_related(
                'transfer',
                'source_branch',
                'destination_branch'
            ).all()
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        product_transfer = serializer.save(company=company)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=product_transfer.reference_number).success(
            f"ProductTransfer '{product_transfer.reference_number}' created by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        product_transfer = serializer.save()
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=product_transfer.reference_number).info(
            f"ProductTransfer '{product_transfer.reference_number}' updated by {identifier}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=instance.reference_number).warning(
            f"ProductTransfer '{instance.reference_number}' deleted by {identifier}."
        )
        instance.delete()


    
    @action(detail=True, methods=["post"], url_path="attach-to-transfer", url_name="attach-to-transfer",)
    def attach_to_transfer(self, request, pk=None):
        product_transfer = self.get_object()
        transfer_id = request.data.get("transfer_id")

        try:
            transfer = Transfer.objects.get(id=transfer_id)
            ProductTransferService.attach_to_transfer(product_transfer, transfer)
        except (Transfer.DoesNotExist, ProductTransferError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(product_transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=["post"], url_path="detach-from-transfer", url_name="detach-from-transfer",)
    def detach_from_transfer(self, request, pk=None):
        product_transfer = self.get_object()

        try:
            ProductTransferService.detach_from_transfer(product_transfer)
        except ProductTransferError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(product_transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    @action(detail=True, methods=["post"], url_path="transfer", url_name="transfer",)
    def transfer(self, request, pk=None):
        product_transfer = self.get_object()

        try:
            ProductTransferService.transfer_product(product_transfer)
        except ProductTransferError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(product_transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)