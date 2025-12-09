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
            return f"Error: {e}"

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
