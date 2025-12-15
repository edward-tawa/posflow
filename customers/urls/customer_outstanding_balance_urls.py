from django.urls import path
from rest_framework.routers import DefaultRouter
from customers.views.customer_outstanding_balance_views import CustomerOutstandingBalanceView


urlpatterns = [
    path('customers/<int:customer_id>/outstanding-balance', CustomerOutstandingBalanceView.as_view(), name='customer-outstanding-balance')
]