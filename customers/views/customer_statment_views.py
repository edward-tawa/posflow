from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger
from datetime import datetime

from customers.services.customer_credit_service import CustomerCreditService
from customers.models.customer_model import Customer
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)


class CustomerStatementView(APIView):
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [ManageCustomersPermission]

    def get(self, request, customer_id, *args, **kwargs):
        """
        Retrieve the statement for a given customer within an optional date range.
        Query params: start_date, end_date (YYYY-MM-DD)
        """
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Optional: validate date format
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            statement = CustomerCreditService.get_customer_statement(customer, start_date, end_date)
            return Response(
                {"customer_id": customer_id, "statement": statement},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error retrieving statement for Customer ID {customer_id} "
                         f"({start_date} - {end_date}): {e}")
            return Response(
                {"error": "An error occurred while retrieving the customer statement."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
