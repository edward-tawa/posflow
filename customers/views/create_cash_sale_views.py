from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger
from drf_yasg.utils import swagger_auto_schema
from customers.services.customer_cash_service import CustomerCashService
from customers.models.customer_model import Customer
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from customers.serializers.customer_service_amount_serializer import AmountSerializer
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)


class CreateCashSaleView(APIView):
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [ManageCustomersPermission]

    @swagger_auto_schema(request_body=AmountSerializer)
    def post(self, request, customer_id, *args, **kwargs):
        """
        Create a cash sale for a specific customer.
        """
        serializer = AmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]

        try:
            customer = Customer.objects.get(id=customer_id, company = request.user.company)
            logger.info(customer)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            CustomerCashService.create_cash_sale(customer, amount)
            return Response(
                {"message": f"Cash sale of {amount} created for customer {customer.first_name}."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Error creating cash sale for Customer ID {customer_id}: {e}")
            return Response(
                {"error": "An error occurred while creating the cash sale."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
