from django.urls import path
from rest_framework.routers import DefaultRouter
from customers.views.customer_credit_limit_views import CustomerCreditLimitView


urlpatterns = [
    path('customers/<int:customer_id>/credit-limit', CustomerCreditLimitView.as_view(), name='customer-credit-limit')
]