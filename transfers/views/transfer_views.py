from rest_framework.viewsets import ModelViewSet
from transfers.models.transfer_model import Transfer
from transfers.serializers.transfer_serializer import TransferSerializer
from config.permissions.company_role_base_permission import CompanyRolePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from company.models.company_model import Company
from config.pagination.pagination import StandardResultsSetPagination
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from rest_framework.decorators import action
from transfers.services.transfer_service import TransferService
from loguru import logger



class TransferViewSet(ModelViewSet):
    """
    ViewSet for managing Transfers (Cash & Product) within a company.
    Provides CRUD operations with strict company-based permissions.
    """
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]
    permission_classes = [CompanyRolePermission]

    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        'reference_number',
        'transfer_date',
        'type',
        'status',
        'notes',
    ]

    ordering_fields = [
        'transfer_date',
        'created_at',
        'updated_at',
        'status',
    ]

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Limit transfers to the logged-in user's company.
            Preload related users for performance.
            """
            return get_company_queryset(self.request, Transfer).select_related(
                'company',
                'transferred_by',
                'received_by',
                'sent_by'
            ).all()
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (
            user if isinstance(user, Company) else None
        )
        transfer = serializer.save(company=company)

        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=transfer.reference_number).success(
            f"Transfer '{transfer.reference_number}' created by {identifier}."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (
            user if isinstance(user, Company) else None
        )
        transfer = serializer.save()

        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=transfer.reference_number).info(
            f"Transfer '{transfer.reference_number}' updated by {identifier}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (
            user if isinstance(user, Company) else None
        )
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'

        logger.bind(reference_number=instance.reference_number).warning(
            f"Transfer '{instance.reference_number}' deleted by {identifier}."
        )

        instance.delete()



    @action(detail=True, methods=["post"], url_path="update-status", url_name="update-status",)
    def update_status(self, request, pk=None):
        transfer = self.get_object()
        new_status = request.data.get("status")

        try:
            TransferService.update_transfer_status(
                transfer=transfer,
                new_status=new_status
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"status": transfer.status},
            status=status.HTTP_200_OK
        )
    

    @action(detail=True, methods=["post"], url_path="recalculate-total", url_name="recalculate-total")
    def recalculate_total(self, request, pk=None):
        transfer = self.get_object()

        TransferService.recalculate_total(transfer)

        return Response(
            {"total_amount": transfer.total_amount},
            status=status.HTTP_200_OK
        )


    @action(detail=True, methods=["post"], url_path="hold", url_name="hold")
    def hold(self, request, pk=None):
        transfer = self.get_object()

        try:
            TransferService.hold_transfer(transfer)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": transfer.status},
            status=status.HTTP_200_OK
        )
    

    @action(detail=True, methods=["post"], url_path="release", url_name="release")
    def release(self, request, pk=None):
        transfer = self.get_object()

        try:
            TransferService.release_transfer(transfer)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": transfer.status},
            status=status.HTTP_200_OK
        )
        

    
    @action(detail=True, methods=["post"], url_path="perform-product-transfer", url_name="perform-product-transfer")
    def perform_product_transfer(self, request, pk=None):
        transfer = self.get_object()

        try:
            TransferService.perform_product_transfer(transfer)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(transfer)
        return Response(serializer.data, status=status.HTTP_200_OK)
