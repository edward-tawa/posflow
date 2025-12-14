from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from customers.services.customer_credit_service import CustomerCreditService
from customers.models.customer_model import Customer
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from customers.serializers.customer_service_amount_serializer import AmountSerializer
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)
from loguru import logger


class RecordCustomerPaymentView(APIView):
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [ManageCustomersPermission]

    def post(self, request, customer_id, *args, **kwargs):
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            CustomerCreditService.record_customer_payment(customer, amount)

            return Response(
                {"message": f"Payment of {amount} recorded for customer {customer.first_name}."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error recording customer payment: {e}")
            return Response(
                {"error": "An error occurred while recording the payment."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
