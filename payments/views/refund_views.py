from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models.refund_model import Refund
from payments.serializers.refund_serializer import RefundSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from payments.services.refund_service import RefundService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class RefundViewSet(ModelViewSet):
    """
    ViewSet for managing Refunds.
    Supports listing, retrieving, creating, updating, and deleting refunds.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'refund_number',
        'company__name',
        'branch__name',
        'payment__payment_number',
        'processed_by__name',
        'reason',
        'notes'
    ]
    ordering_fields = ['created_at', 'updated_at', 'refund_date', 'amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, Refund).select_related(
                'company', 'branch', 'payment', 'processed_by'
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"Refund '{refund.refund_number}' created by '{actor}' "
            f"for company '{refund.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"Refund '{refund.refund_number}' updated by '{actor}' "
            f"for company '{refund.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund_number = instance.refund_number
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"Refund '{refund_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )

    
    @action(detail=True, methods=['post'], url_path='process')
    def process_refund(self, request, pk=None):
        refund = self.get_object()
        RefundService.mark_refund_as_processed(refund)
        return Response({"status": "processed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='fail')
    def fail_refund(self, request, pk=None):
        refund = self.get_object()
        RefundService.mark_refund_as_failed(refund)
        return Response({"status": "failed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='pending')
    def pending_refund(self, request, pk=None):
        refund = self.get_object()
        RefundService.mark_refund_as_pending(refund)
        return Response({"status": "pending"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_refund_action(self, request, pk=None):
        refund = self.get_object()
        RefundService.cancel_refund(refund)
        return Response({"status": "cancelled"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        refund = self.get_object()
        new_status = request.data.get("status")
        RefundService.update_refund_status(refund, new_status)
        return Response({"status": new_status}, status=status.HTTP_200_OK)

    # -------------------------
    # RELATION ACTIONS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='attach-payment')
    def attach_payment(self, request, pk=None):
        refund = self.get_object()
        payment_id = request.data.get("payment_id")
        RefundService.attach_to_payment(refund, payment_id)
        return Response({"payment_id": payment_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-payment')
    def detach_payment(self, request, pk=None):
        refund = self.get_object()
        RefundService.detach_from_payment(refund)
        return Response({"payment_detached": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='attach-order')
    def attach_order(self, request, pk=None):
        refund = self.get_object()
        order_id = request.data.get("order_id")
        RefundService.attach_to_order(refund, order_id)
        return Response({"order_id": order_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-order')
    def detach_order(self, request, pk=None):
        refund = self.get_object()
        RefundService.detach_from_order(refund)
        return Response({"order_detached": True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='attach-customer')
    def attach_customer(self, request, pk=None):
        refund = self.get_object()
        customer_id = request.data.get("customer_id")
        RefundService.attach_refund_to_customer(refund, customer_id)
        return Response({"customer_id": customer_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-customer')
    def detach_customer(self, request, pk=None):
        refund = self.get_object()
        RefundService.detach_refund_from_customer(refund)
        return Response({"customer_detached": True}, status=status.HTTP_200_OK)
