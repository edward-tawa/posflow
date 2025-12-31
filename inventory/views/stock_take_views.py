from rest_framework.viewsets import ModelViewSet
from inventory.models.stock_take_model import StockTake
from inventory.serializers.stock_take_serializer import StockTakeSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from inventory.services.stock_take_service import StockTakeService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from loguru import logger


class StockTakeViewSet(ModelViewSet):
    """
    Handles creating, listing, updating, and deleting stocktakes.
    Logs all critical user actions for traceability.
    """
    queryset = StockTake.objects.all()
    serializer_class = StockTakeSerializer
    permission_classes = [InventoryPermission]
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['reference_number', 'performed_by__username', 'performed_by__first_name', 'performed_by__last_name', 'status']
    ordering_fields = ['stock_take_date', 'created_at', 'updated_at', 'status'] #removed `counted` at field doesnot exist replace with `stock_take_date`
    ordering = ['stock_take_date']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthorized access attempt to StockTakeViewSet.")
                return StockTake.objects.none()

            company = getattr(user, 'company', None)
            if company:
                logger.info(f"User '{user.username}' retrieved stocktakes for company '{company.name}'.")
                return StockTake.objects.filter(company=company)
            logger.warning(f"User '{user.username}' has no associated company. Returning empty queryset.")
            return StockTake.objects.none()
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    def perform_create(self, serializer):
        logger.info(self.request.user.branch)
        stock_take = serializer.save(
            company = self.request.user.company, 
            branch = self.request.user.branch, 
            performed_by = self.request.user
        )
        user = self.request.user
        logger.success(
            f"StockTake created by '{user.username}' ({user.role}) "
            f"for company '{stock_take.company.name}' "
            f"at branch '{stock_take.branch.name}' "
            f"with reference '{stock_take.reference_number}'."
        )

    def perform_update(self, serializer):
        stock_take = serializer.save()
        user = self.request.user
        logger.info(
            f"StockTake '{stock_take.reference_number}' updated by '{user.username}' ({user.role}). "
            f"Status: {stock_take.status}."
        )

    def perform_destroy(self, instance):
        ref = instance.reference_number
        company_name = instance.company.name
        user = self.request.user
        instance.delete()
        logger.warning(
            f"StockTake '{ref}' deleted by '{user.username}' from company '{company_name}'."
        )



    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        new_status = request.data.get("status")
        try:
            stock_take = self.get_object()
            updated = StockTakeService.update_stock_take_status(stock_take, new_status)
            serializer = self.get_serializer(updated)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="update-quantity")
    def update_quantity(self, request, pk=None):
        new_quantity = request.data.get("quantity_counted")
        try:
            new_quantity = int(new_quantity)
            stock_take = self.get_object()
            updated = StockTakeService.update_quantity_counted(stock_take, new_quantity)
            serializer = self.get_serializer(updated)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        stock_take = self.get_object()
        try:
            approved = StockTakeService.approve_stock_take(stock_take, request.user)
            serializer = self.get_serializer(approved)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        reason = request.data.get("reason", "")
        stock_take = self.get_object()
        try:
            rejected = StockTakeService.reject_stock_take(stock_take, request.user, reason)
            serializer = self.get_serializer(rejected)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="finalize")
    def finalize(self, request, pk=None):
        stock_take = self.get_object()
        try:
            finalized = StockTakeService.finalize_stock_take(stock_take)
            serializer = self.get_serializer(finalized)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)