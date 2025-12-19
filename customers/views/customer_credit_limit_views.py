from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger
from customers.services.customer_credit_service import CustomerCreditService
from customers.models.customer_model import Customer
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from customers.serializers.customer_service_amount_serializer import AmountSerializer
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)
from drf_yasg.utils import swagger_auto_schema

class CustomerCreditLimitView(APIView):
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [ManageCustomersPermission]
    @swagger_auto_schema(request_body=AmountSerializer)
    def post(self, request, customer_id, *args, **kwargs):
        """
        Set or create credit limit for a customer.
        """
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            CustomerCreditService.set_customer_credit_limit(customer, amount)
            return Response(
                {"message": f"Credit limit of {amount} set for customer {customer.first_name}."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Error setting credit limit for Customer ID {customer_id}: {e}")
            return Response(
                {"error": "An error occurred while setting the credit limit."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, customer_id, *args, **kwargs):
        """
        Update existing credit limit for a customer.
        """
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            CustomerCreditService.update_customer_credit_limit(customer, amount)
            return Response(
                {"message": f"Credit limit updated to {amount} for customer {customer.first_name}."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error updating credit limit for Customer ID {customer_id}: {e}")
            return Response(
                {"error": "An error occurred while updating the credit limit."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
