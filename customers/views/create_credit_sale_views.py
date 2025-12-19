from customers.services.customer_credit_service import CustomerCreditService
from customers.models.customer_model import Customer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from branch.models.branch_model import Branch
from customers.models.customer_branch_history_model import CustomerBranchHistory
from customers.serializers.customer_branch_history_serializer import CustomerBranchHistorySerializer
from customers.serializers.customer_service_amount_serializer import AmountSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_company_or_user_company import get_expected_company
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from loguru import logger
from drf_yasg.utils import swagger_auto_schema



class CreateCreditSaleView(APIView):
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [ManageCustomersPermission]
    @swagger_auto_schema(request_body=AmountSerializer)
    def post(self, request, customer_id, *args, **kwargs):
        serializer = AmountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = serializer.validated_data['amount']
            customer = Customer.objects.get(id=customer_id)

            CustomerCreditService.create_credit_sale(customer, amount)

            return Response(
                {"message": f"Credit sale of {amount} created for customer {customer.first_name}."},
                status=status.HTTP_201_CREATED
            )

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error creating credit sale: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
