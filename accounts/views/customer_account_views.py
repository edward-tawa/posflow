from rest_framework.viewsets import ModelViewSet
from accounts.models.customer_account import CustomerAccount
from customers.models.customer_model import Customer
from accounts.serializers.customer_account_serializer import CustomerAccountSerializer
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
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from accounts.services.accounts_service import AccountsService
from company.models.company_model import Company
from django.core.exceptions import ObjectDoesNotExist
from loguru import logger


class CustomerAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Customer Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = CustomerAccount.objects.all()
    serializer_class = CustomerAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['customer__first_name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'customer__first_name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return CustomerAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, CustomerAccount).select_related('customer', 'account')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        customer_account = serializer.save(company=company)#Add replace company with branch
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(customer=customer_account.customer.first_name, account_number=customer_account.account.account_number).success(
            f"CustomerAccount for customer '{customer_account.customer.first_name}' and account '{customer_account.account.name}' (Number: {customer_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        customer_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(customer=customer_account.customer.name, account_number=customer_account.account.number).info(
            f"CustomerAccount for customer '{customer_account.customer.name}' and account '{customer_account.account.name}' (Number: {customer_account.account.number}) updated by {actor}."
        )
        
    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(customer=instance.customer.name, account_number=instance.account.number).warning(
            f"CustomerAccount for customer '{instance.customer.name}' and account '{instance.account.name}' (Number: {instance.account.number}) deleted by {actor}."
        )
        instance.delete()

    




class GetCustomerAccountTransactions(APIView):
    """
    API View to retrieve transactions for a specific customer.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [ManageCustomersPermission, IsAuthenticated]

    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {customer_id} does not exist.")
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        
         # Check permissions
        if not ManageCustomersPermission().has_object_permission(request, self, customer):
            logger.warning(f"Unauthorized access attempt to Account ID {customer_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch transactions
        customer_transactions = Transaction.objects.filter(
                                    customer=customer,
                                    company=request.user.company,
                                    branch=user_branch
                                )
        serializer = TransactionSerializer(customer_transactions, many=True)

        logger.info(
            f"Retrieved {len(customer_transactions)} transactions "
            f"for Account ID {customer_id} by user {request.user}."
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class GetCustomerAccountBalance(APIView):
    """
    API View to retrieve the balance of a specific customer's branch account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [ManageCustomersPermission, IsAuthenticated]

    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {customer_id} does not exist.")
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not ManageCustomersPermission().has_object_permission(request, self, customer):
            logger.warning(f"Unauthorized access attempt to Account ID {customer_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # validate user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User must be linked to a branch."}, status=status.HTTP_403_FORBIDDEN)
        customer_account = CustomerAccount.objects.filter(
            customer=customer, branch=user_branch, company=request.user.company).first()
        if not customer_account:
            logger.warning(f"CustomerAccount not found for Customer {customer_id}.")
            return Response({"detail": "CustomerAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        balance = customer_account.account.balance
        logger.info(f"Retrieved balance for Account ID {customer_id} by user {request.user}: {balance}")
        return Response({"account_id": customer_id, "balance": balance}, status=status.HTTP_200_OK)
    


class FreezeCustomerAccount(APIView):
    """
    API View to freeze a specific customer account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [ManageCustomersPermission, IsAuthenticated]

    def post(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {customer_id} does not exist.")
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not ManageCustomersPermission().has_object_permission(request, self, customer):
            logger.warning(f"Unauthorized freeze attempt on Customer ID {customer_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        
        customer_account = CustomerAccount.objects.filter(customer=customer,
                                                           branch=user_branch, company=request.user.company).first()
        if not customer_account:
            logger.warning(f"CustomerAccount not found for Customer {customer_id} and Branch {user_branch.id}.")
            return Response({"detail": "CustomerAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        customer_account.account.is_frozen = True
        try:
            customer_account.account.save(update_fields=['is_frozen'])
        except Exception as e:
            logger.error(f"Failed to freeze Account {customer_id}: {e}")
            return Response({"detail": f"Failed to freeze account {customer_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(f"CustomerAccount ID {customer_id} frozen by user {request.user}.")
        return Response({"detail": f"CustomerAccount {customer_id} has been frozen."}, status=status.HTTP_200_OK)
    


class UnfreezeCustomerAccount(APIView):
    """
    API View to unfreeze a specific customer account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [ManageCustomersPermission, IsAuthenticated]

    def post(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {customer_id} does not exist.")
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        if not ManageCustomersPermission().has_object_permission(request, self, customer):
            logger.warning(f"Unauthorized unfreeze attempt on Customer ID {customer_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        customer_account = CustomerAccount.objects.filter(customer=customer, branch=user_branch, company=request.user.company).first()
        if not customer_account:
            logger.warning(f"CustomerAccount not found for Customer {customer_id} and Branch {user_branch.id}.")
            return Response({"detail": "CustomerAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            AccountsService.unfreeze_account(customer_account.account)
        except Exception as e:
            logger.error(f"Failed to unfreeze Account {customer_account.account.id}: {e}")
            return Response({"detail": f"Failed to unfreeze account {customer_account.id} for customer {customer_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Account ID {customer_id} unfrozen by user {request.user}.")
        return Response(
            {"detail": f"Account {customer_account.account.id} has been unfrozen.", "is_frozen": False}, 
            status=status.HTTP_200_OK
        )

        