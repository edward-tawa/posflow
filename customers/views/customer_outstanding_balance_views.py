from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger

from customers.services.customer_credit_service import CustomerCreditService
from customers.models.customer_model import Customer
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)


class CustomerOutstandingBalanceView(APIView):
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [ManageCustomersPermission]

    def get(self, request, customer_id, *args, **kwargs):
        """
        Retrieve the outstanding balance for a given customer.
        """
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            outstanding_balance = CustomerCreditService.get_customer_outstanding_balance(customer)
            return Response(
                {"customer_id": customer_id, "outstanding_balance": outstanding_balance},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error retrieving outstanding balance for Customer ID {customer_id}: {e}")
            return Response(
                {"error": "An error occurred while retrieving the outstanding balance."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
