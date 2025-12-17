from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models import Expense
from payments.serializers.expense_serializer import ExpenseSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from payments.services.expense_service import ExpenseService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class ExpenseViewSet(ModelViewSet):
    """
    ViewSet for managing Expenses.
    Supports listing, retrieving, creating, updating, and deleting expenses.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'expense_number',
        'company__name',
        'branch__name',
        'incurred_by__name',
        'description'
    ]
    ordering_fields = ['created_at', 'updated_at', 'expense_date', 'amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, Expense).select_related(
                'company', 'branch', 'incurred_by'
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        expense = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"Expense '{expense.expense_number}' created by '{actor}' "
            f"for company '{expense.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        expense = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"Expense '{expense.expense_number}' updated by '{actor}' "
            f"for company '{expense.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        expense_number = instance.expense_number
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"Expense '{expense_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )



    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        expense = self.get_object()
        ExpenseService.mark_expense_as_paid(expense)
        return Response({"status": "PAID"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-unpaid')
    def mark_unpaid(self, request, pk=None):
        expense = self.get_object()
        ExpenseService.mark_expense_as_unpaid(expense)
        return Response({"status": "UPAID"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        expense = self.get_object()
        new_status = request.data.get("status")
        ExpenseService.update_expense_status(expense, new_status)
        return Response({"status": new_status}, status=status.HTTP_200_OK)

    # -------------------------
    # PAYMENT RELATION ACTIONS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='attach-payment')
    def attach_payment(self, request, pk=None):
        expense = self.get_object()
        payment_id = request.data.get("payment_id")
        ExpenseService.attach_expense_to_payment(expense, payment_id)
        return Response({"payment_id": payment_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-payment')
    def detach_payment(self, request, pk=None):
        expense = self.get_object()
        ExpenseService.detach_expense_from_payment(expense)
        return Response({"payment_detached": True}, status=status.HTTP_200_OK)