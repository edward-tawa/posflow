from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models import PaymentAllocation
from payments.serializers.payment_allocation_serializer import PaymentAllocationSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from payments.services.payment_allocation.payment_allocation_service import PaymentAllocationService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PaymentAllocationViewSet(ModelViewSet):
    """
    ViewSet for managing PaymentAllocations.
    Supports listing, retrieving, creating, updating, and deleting allocations.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PaymentAllocation.objects.all()
    serializer_class = PaymentAllocationSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'allocation_number',
        'company__name',
        'branch__name',
        'payment__payment_number'
    ]
    ordering_fields = ['created_at', 'updated_at', 'allocation_date', 'amount_allocated']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, PaymentAllocation).select_related(
                'company', 'branch', 'payment'
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        allocation = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PaymentAllocation '{allocation.allocation_number}' created by '{actor}' "
            f"for company '{allocation.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        allocation = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PaymentAllocation '{allocation.allocation_number}' updated by '{actor}' "
            f"for company '{allocation.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        allocation_number = instance.allocation_number
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PaymentAllocation '{allocation_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )


    @action(detail=True, methods=['post'], url_path='apply')
    def apply_allocation(self, request, pk=None):
        allocation = self.get_object()
        PaymentAllocationService.apply_allocation(allocation)
        return Response({"status": "APPLIED"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reverse')
    def reverse_allocation(self, request, pk=None):
        allocation = self.get_object()
        reason = request.data.get("reason")
        PaymentAllocationService.reverse_allocation(allocation, reason=reason)
        return Response({"status": "REVERSED"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        allocation = self.get_object()
        new_status = request.data.get("status")
        PaymentAllocationService.update_payment_allocation_status(allocation, new_status)
        return Response({"status": new_status}, status=status.HTTP_200_OK)

    # -------------------------
    # RELATION ACTIONS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='attach-customer')
    def attach_customer(self, request, pk=None):
        allocation = self.get_object()
        customer_id = request.data.get("customer_id")
        PaymentAllocationService.attach_allocation_to_customer(allocation, customer_id)
        return Response({"customer_id": customer_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-customer')
    def detach_customer(self, request, pk=None):
        allocation = self.get_object()
        PaymentAllocationService.detach_allocation_from_customer(allocation)
        return Response({"customer_detached": True}, status=status.HTTP_200_OK)

    # -------------------------
    # DELETE ACTION
    # -------------------------
    @action(detail=True, methods=['post'], url_path='delete')
    def delete_allocation(self, request, pk=None):
        allocation = self.get_object()
        PaymentAllocationService.delete_payment_allocation(allocation)
        return Response({"deleted": True}, status=status.HTTP_200_OK)