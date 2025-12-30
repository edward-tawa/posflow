from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from customers.models.customer_model import Customer
from customers.serializers.customer_serializer import CustomerSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from customers.permissions.manage_customers_permission import ManageCustomersPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from users.models.user_model import User
from company.models.company_model import Company

class CustomerViewSet(ModelViewSet):
    """
    ViewSet for viewing customers.
    Supports listing and retrieving customer details.
    """
   
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [UserCookieJWTAuthentication, JWTAuthentication, CompanyCookieJWTAuthentication]
    permission_classes = [ManageCustomersPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['first_name', 'last_name', 'email', 'last_purchase_date']
    ordering = ['last_name', 'first_name']  # Default ordering


    def get_queryset(self):
        """
        Optionally restricts the returned customers to a given company,
        by filtering against a `company_id` query parameter in the URL.
        """
        staff_roles = ['Manager', 'Sales', 'Marketing', 'Inventory', 'Accountant', 'Admin']
        current = self.request.user
        if not current.is_authenticated:
            return Customer.objects.none()
        
        if isinstance(current, User):
            if current.is_staff or current.is_superuser or current.role in staff_roles:
                return Customer.objects.filter(company=current.company)
        elif isinstance(current, Company):
            return Customer.objects.filter(company=current)
        return Customer.objects.none()
        