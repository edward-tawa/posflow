from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from loans.models import Loan
from loans.permissions.loan_permissions import LoanPermissions
from loans.serializers.loan_serializer import LoanSerializer
from loguru import logger
from rest_framework.permissions import AllowAny, IsAuthenticated


class LoanViewSet(ModelViewSet):
    """
    ViewSet for managing Loans.
    Supports listing, retrieving, creating, updating, and deleting loans.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [LoanPermissions]  # Add permissions

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'borrower__first_name',
        'issued_by__first_name',
        'notes'
    ]
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'end_date', 'loan_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns the Loan queryset filtered by the logged-in company.
            """
            company = get_company_queryset(self.request, Loan)
            logger.info(company)
            return Loan.objects.all().select_related('borrower', 'issued_by')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        Saves a new Loan instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        loan = serializer.save(issued_by = self.request.user)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"Loan '{loan.id}' created by '{actor}' "
            f"for borrower '{loan.borrower.first_name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated Loan instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        loan = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"Loan '{loan.id}' updated by '{actor}' "
            f"for borrower '{loan.borrower.first_name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a Loan instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        loan_id = instance.id
        borrower_name = instance.borrower.first_name
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"Loan '{loan_id}' for borrower '{borrower_name}' deleted by '{actor}'."
        )
