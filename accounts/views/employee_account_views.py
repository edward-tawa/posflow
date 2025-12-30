from rest_framework.viewsets import ModelViewSet
from accounts.models.customer_account_model import CustomerAccount
from accounts.models.employee_account_model import EmployeeAccount
from accounts.serializers.employee_account_serializer import EmployeeAccountSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models.transaction_model import Transaction
from transactions.serializers.transaction_serializer import TransactionSerializer
from accounts.models.account_model import Account
from accounts.serializers.account_serializer import AccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_account_company_queryset
from accounts.permissions.account_permission import AccountPermissionAccess
from users.permissions.user_permissions import UserPermissions
from accounts.services.account_service import AccountsService
from company.models.company_model import Company
from users.models.user_model import User
from django.core.exceptions import ObjectDoesNotExist
from loguru import logger


class EmployeeAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Employee Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = EmployeeAccount.objects.all()
    serializer_class = EmployeeAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['employee__first_name', 'account__name', 'account__account_number']
    ordering_fields = ['created_at', 'updated_at', 'employee__first_name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return EmployeeAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, EmployeeAccount).select_related('employee', 'account')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        employee_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(employee=employee_account.employee.first_name, account_number=employee_account.account.account_number).success(
            f"EmployeeAccount for employee '{employee_account.employee.first_name}' and account '{employee_account.account.name}' (Number: {employee_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        employee_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(employee=employee_account.employee.first_name, account_number=employee_account.account.account_number).info(
            f"EmployeeAccount for employee '{employee_account.employee.first_name}' and account '{employee_account.account.name}' (Number: {employee_account.account.account_number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(employee=instance.employee.first_name, account_number=instance.account.account_number).warning(
            f"EmployeeAccount for employee '{instance.employee.first_name}' and account '{instance.account.name}' (Number: {instance.account.account_number}) deleted by {actor}."
        )
        instance.delete()






class GetEmployeeAccountTransactions(APIView):
    """
    API View to retrieve transactions for a specific employee.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess, IsAuthenticated]

    def get(self, request, user_id):
        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Employee with ID {user_id} does not exist.")
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        if not UserPermissions().has_object_permission(request, self, employee):
            logger.warning(f"Unauthorized access attempt to Account ID {user_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch transactions
        employee_transactions = Transaction.objects.filter(
                                    employee=employee,
                                    company=request.user.company,
                                    branch=user_branch
                                )
        serializer = TransactionSerializer(employee_transactions, many=True)
        logger.info(
            f"Retrieved {len(employee_transactions)} transactions "
            f"for Account ID {user_id} by user {request.user.username}."
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class GetEmployeeAccountBalance(APIView):
    """
    API View to retrieve the balance of a specific employee account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess, IsAuthenticated]

    def get(self, request, user_id):
        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Employee with ID {user_id} does not exist.")
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not UserPermissions().has_object_permission(request, self, employee):
            logger.warning(f"Unauthorized access attempt to Account ID {user_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # validate user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User must be linked to a branch."}, status=status.HTTP_403_FORBIDDEN)
        employee_account = EmployeeAccount.objects.filter(
            employee=employee, branch=user_branch, company=request.user.company).first()
        if not employee_account:
            logger.warning(f"EmployeeAccount not found for Employee {user_id}.")
            return Response({"detail": "EmployeeAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        balance = employee_account.account.balance
        logger.info(f"Retrieved balance for Account ID {user_id} by user {request.user.username}: {balance}")
        return Response({"account_id": user_id, "balance": balance}, status=status.HTTP_200_OK)
    


class FreezeEmployeeAccount(APIView):
    """
    API View to freeze a specific employee account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess, IsAuthenticated]

    def post(self, request, user_id):
        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Employee with ID {user_id} does not exist.")
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not UserPermissions().has_object_permission(request, self, employee):
            logger.warning(f"Unauthorized freeze attempt on Employee ID {user_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"Employee {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        
        employee_account = EmployeeAccount.objects.filter(employee=employee,
                                                           branch=user_branch, company=request.user.company).first()
        if not employee_account:
            logger.warning(f"EmployeeAccount not found for Employee {user_id} and Branch {user_branch.id}.")
            return Response({"detail": "EmployeeAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        employee_account.account.is_frozen = True
        try:
            employee_account.account.save(update_fields=['is_frozen'])
        except Exception as e:
            logger.error(f"Failed to freeze Account {user_id}: {e}")
            return Response({"detail": f"Failed to freeze account {user_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(f"EmployeeAccount ID {user_id} frozen by user {request.user.username}.")
        return Response({"detail": f"EmployeeAccount {user_id} has been frozen."}, status=status.HTTP_200_OK)
    


class UnfreezeEmployeeAccount(APIView):
    """
    API View to unfreeze a specific employee account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess, IsAuthenticated]

    def post(self, request, user_id):
        try:
            employee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Employee with ID {user_id} does not exist.")
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        if not UserPermissions().has_object_permission(request, self, employee):
            logger.warning(f"Unauthorized unfreeze attempt on Employee ID {user_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        employee_account = EmployeeAccount.objects.filter(employee=employee, branch=user_branch, company=request.user.company).first()
        if not employee_account:
            logger.warning(f"EmployeeAccount not found for Employee {user_id} and Branch {user_branch.id}.")
            return Response({"detail": "EmployeeAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            AccountsService.unfreeze_account(employee_account.account)
        except Exception as e:
            logger.error(f"Failed to unfreeze Account {employee_account.account.id}: {e}")
            return Response({"detail": f"Failed to unfreeze account {employee_account.id} for employee {user_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Account ID {user_id} unfrozen by user {request.user.username}.")
        return Response(
            {"detail": f"Account {employee_account.account.id} has been unfrozen.", "is_frozen": False}, 
            status=status.HTTP_200_OK
        )