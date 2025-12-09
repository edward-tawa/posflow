from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from branch.models.branch_model import Branch
from customers.models.customer_branch_history_model import CustomerBranchHistory
from customers.serializers.customer_branch_history_serializer import CustomerBranchHistorySerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_company_or_user_company import get_expected_company
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from loguru import logger

class CustomerBranchHistoryViewSet(ModelViewSet):
    """
    ViewSet for managing CustomerBranchHistory.
    Supports listing, retrieving, creating, updating, and deleting.
    Includes filtering, searching, ordering, company validation, and logging.
    """

    queryset = CustomerBranchHistory.objects.all()
    serializer_class = CustomerBranchHistorySerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    permission_classes = [ManageCustomersPermission]   # permissions

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email', 'branch__name']
    ordering_fields = ['last_visited', 'created_at', 'updated_at']
    ordering = ['-last_visited']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return CustomerBranchHistory for branches belonging to the logged-in user's company."""
            return (
                get_company_queryset(self.request, CustomerBranchHistory)
                .select_related('branch', 'customer')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """Create CustomerBranchHistory with company enforcement and logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        # Save with enforced company context (via branch/customer validation)
        history = serializer.save()

        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.success(
            f"CustomerBranchHistory for customer '{history.customer.email}' at branch '{history.branch.name}' "
            f"created by {actor}."
        )

    def perform_update(self, serializer):
        """Update CustomerBranchHistory with company validation and logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        history = serializer.save()
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.info(
            f"CustomerBranchHistory for customer '{history.customer.email}' at branch '{history.branch.name}' "
            f"updated by {actor}."
        )
