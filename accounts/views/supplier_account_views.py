from rest_framework.viewsets import ModelViewSet
from accounts.models.supplier_account_model import SupplierAccount
from accounts.serializers.supplier_account_serializer import SupplierAccountSerializer
from suppliers.models.supplier_model import Supplier
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
from suppliers.permissions.supplier_permissions import SupplierPermissions
from accounts.services.account_service import AccountsService
from company.models.company_model import Company
from django.core.exceptions import ObjectDoesNotExist
from loguru import logger


class SupplierAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Supplier Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = SupplierAccount.objects.all()
    serializer_class = SupplierAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['supplier__name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'supplier__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return SupplierAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, SupplierAccount).select_related('supplier', 'account')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        supplier_account = serializer.save(company=company)#Replace company with branch
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(supplier=supplier_account.supplier.name, account_number=supplier_account.account.account_number).success(
            f"SupplierAccount for supplier '{supplier_account.supplier.name}' and account '{supplier_account.account.name}' (Number: {supplier_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        supplier_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(supplier=supplier_account.supplier.name, account_number=supplier_account.account.account_number).info(
            f"SupplierAccount for supplier '{supplier_account.supplier.name}' and account '{supplier_account.account.name}' (Number: {supplier_account.account.account_number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(supplier=instance.supplier.name, account_number=instance.account.account_number).warning(
            f"SupplierAccount for supplier '{instance.supplier.name}' and account '{instance.account.name}' (Number: {instance.account.account_number}) deleted by {actor}."
        )
        instance.delete()

    




class GetSupplierAccountTransactions(APIView):
    """
    API View to retrieve transactions for a specific supplier.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions, IsAuthenticated]

    def get(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            logger.warning(f"Supplier with ID {supplier_id} does not exist.")
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        
         # Check permissions
        if not SupplierPermissions().has_object_permission(request, self, supplier):
            logger.warning(f"Unauthorized access attempt to Account ID {supplier_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch transactions
        supplier_transactions = Transaction.objects.filter(
                                    supplier=supplier,
                                    company=request.user.company,
                                    branch=user_branch
                                )
        serializer = TransactionSerializer(supplier_transactions, many=True)

        logger.info(
            f"Retrieved {len(supplier_transactions)} transactions "
            f"for Account ID {supplier_id} by user {request.user.username}."
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class GetSupplierAccountBalance(APIView):
    """
    API View to retrieve the balance of a specific supplier's account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions, IsAuthenticated]

    def get(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            logger.warning(f"Supplier with ID {supplier_id} does not exist.")
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not SupplierPermissions().has_object_permission(request, self, supplier):
            logger.warning(f"Unauthorized access attempt to Account ID {supplier_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # validate user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User must be linked to a branch."}, status=status.HTTP_403_FORBIDDEN)
        supplier_account = SupplierAccount.objects.filter(
            supplier=supplier, branch=user_branch, company=request.user.company).first()
        if not supplier_account:
            logger.warning(f"SupplierAccount not found for Supplier {supplier_id}.")
            return Response({"detail": "SupplierAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        balance = supplier_account.account.balance
        logger.info(f"Retrieved balance for Account ID {supplier_id} by user {request.user}: {balance}")
        return Response({"account_id": supplier_id, "balance": balance}, status=status.HTTP_200_OK)
    


class FreezeSupplierAccount(APIView):
    """
    API View to freeze a specific supplier account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions, IsAuthenticated]

    def post(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            logger.warning(f"Supplier with ID {supplier_id} does not exist.")
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not SupplierPermissions().has_object_permission(request, self, supplier):
            logger.warning(f"Unauthorized freeze attempt on Supplier ID {supplier_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        
        supplier_account = SupplierAccount.objects.filter(supplier=supplier,
                                                           branch=user_branch, company=request.user.company).first()
        if not supplier_account:
            logger.warning(f"SupplierAccount not found for Supplier {supplier_id} and Branch {user_branch.id}.")
            return Response({"detail": "SupplierAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        supplier_account.account.is_frozen = True
        try:
            supplier_account.account.save(update_fields=['is_frozen'])
        except Exception as e:
            logger.error(f"Failed to freeze Account {supplier_id}: {e}")
            return Response({"detail": f"Failed to freeze account {supplier_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(f"SupplierAccount ID {supplier_id} frozen by user {request.user.username}.")
        return Response({"detail": f"SupplierAccount {supplier_id} has been frozen."}, status=status.HTTP_200_OK)
    


class UnfreezeSupplierAccount(APIView):
    """
    API View to unfreeze a specific supplier account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions, IsAuthenticated]

    def post(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            logger.warning(f"Supplier with ID {supplier_id} does not exist.")
            return Response({"detail": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

        if not SupplierPermissions().has_object_permission(request, self, supplier):
            logger.warning(f"Unauthorized unfreeze attempt on Supplier ID {supplier_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        supplier_account = SupplierAccount.objects.filter(supplier=supplier, branch=user_branch, company=request.user.company).first()
        if not supplier_account:
            logger.warning(f"SupplierAccount not found for Supplier {supplier_id} and Branch {user_branch.id}.")
            return Response({"detail": "SupplierAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            AccountsService.unfreeze_account(supplier_account.account)
        except Exception as e:
            logger.error(f"Failed to unfreeze Account {supplier_account.account.id}: {e}")
            return Response({"detail": f"Failed to unfreeze account {supplier_account.id} for supplier {supplier_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Account ID {supplier_account.id} unfrozen by user {request.user.username}.")
        return Response(
            {"detail": f"Account {supplier_account.account.id} has been unfrozen.", "is_frozen": False}, 
            status=status.HTTP_200_OK
        )

    

