from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger
from inventory.models.stock_take_approval_model import StockTakeApproval
from inventory.serializers.stock_take_approval_serializer import StockTakeApprovalSerializer
from inventory.models.stock_take_model import StockTake
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from rest_framework.exceptions import ValidationError
from company.models.company_model import Company






class StockTakeApprovalViewSet(ModelViewSet):
    """
    ViewSet for managing Stock Take approvals.
    Includes approval lifecycle enforcement and custom actions.
    """
    queryset = StockTakeApproval.objects.all()
    serializer_class = StockTakeApprovalSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [InventoryPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['stock_take__reference', 'approved_by__email', 'comment']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination


    def get_queryset(self):
        """
        Company-scoped queryset for Stock Take approvals.
        """
        try:
            user = self.request.user
            if not user.is_authenticated:
                return StockTakeApproval.objects.none()

            company = getattr(user, 'company', None) or (
                user if isinstance(user, Company) else None
            )

            if not company:
                return StockTakeApproval.objects.none()

            return (
                StockTakeApproval.objects
                .filter(stock_take__company=company)
                .select_related('stock_take', 'approved_by')
            )

        except Exception as e:
            logger.error(e)
            return self.queryset.none()


    def perform_create(self, serializer):
        user = self.request.user
        stock_take = serializer.validated_data.get('stock_take')

        if StockTakeApproval.objects.filter(stock_take=stock_take).exists():
            logger.warning(
                f"Duplicate approval attempt for StockTake ID {stock_take.id}"
            )
            raise ValidationError("This stock take has already been approved or rejected.")

        if stock_take.is_finalized:
           raise ValidationError("Cannot approve a finalized stock take.")

        approval = serializer.save(approved_by=user)

        logger.success(
            f"StockTake ID {stock_take.id} approved by {user.email}"
        )
    

    def perform_update(self, serializer):
        instance = serializer.instance

        if instance.stock_take.is_finalized:
            raise ValidationError("Finalized stock take approvals cannot be modified.")

        serializer.save()

    def perform_destroy(self, instance):
        if instance.stock_take.is_finalized:
            raise ValidationError("Finalized stock take approvals cannot be deleted.")

        logger.warning(
            f"Approval ID {instance.id} deleted by {self.request.user.email}"
        )
        instance.delete()

    

    @action(detail=False, methods=['post'], url_path='stock-take-approve')
    def approve(self, request):
        stock_take_id = request.data.get('stock_take_id')
        comment = request.data.get('comment', '')

        try:
            stock_take = StockTake.objects.get(
                id=stock_take_id,
                company=getattr(request.user, 'company', None)
                )

            if stock_take.is_finalized:
                return Response(
                    {"detail": "Stock take is already finalized."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if StockTakeApproval.objects.filter(stock_take=stock_take).exists():
                return Response(
                    {"detail": "Stock take already has a decision."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            approval = StockTakeApproval.objects.create(
                stock_take=stock_take,
                approved_by=request.user,
                comment=comment,
            )

            stock_take.status = StockTake.Status.APPROVED
            stock_take.is_finalized = True
            stock_take.save(update_fields=['status', 'is_finalized'])

            logger.success(
                f"StockTake ID {stock_take.id} APPROVED by {request.user.email}"
            )

            return Response(
                StockTakeApprovalSerializer(
                    approval, context={'request': request}
                ).data,
                status=status.HTTP_200_OK,
            )

        except StockTake.DoesNotExist:
            return Response(
                {"detail": "Stock take not found."},
                status=status.HTTP_404_NOT_FOUND,
            )



    @action(detail=False, methods=['post'], url_path='reject')
    def reject(self, request):
        stock_take_id = request.data.get('stock_take_id')
        comment = request.data.get('comment')

        if not comment:
            return Response(
                {"detail": "Rejection requires a comment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            stock_take = StockTake.objects.get(
                id=stock_take_id,
                company=getattr(request.user, 'company', None)
                )

            if stock_take.is_finalized:
                return Response(
                    {"detail": "Stock take is already finalized."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            approval = StockTakeApproval.objects.create(
                stock_take=stock_take,
                approved_by=request.user,
                comment=comment,
            )

            stock_take.status = StockTake.Status.REJECTED
            stock_take.is_finalized = True
            stock_take.save(update_fields=['status', 'is_finalized'])

            logger.warning(
                f"StockTake ID {stock_take.id} REJECTED by {request.user.email}"
            )

            return Response(
                StockTakeApprovalSerializer(
                    approval, context={'request': request}
                ).data,
                status=status.HTTP_200_OK,
            )

        except StockTake.DoesNotExist:
            return Response(
                {"detail": "Stock take not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


