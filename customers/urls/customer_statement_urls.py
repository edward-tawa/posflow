from django.urls import path
from rest_framework.routers import DefaultRouter
from customers.views.customer_statment_views import CustomerStatementView


urlpatterns = [
    path('customers/<int:customer_id>/statement', CustomerStatementView.as_view(), name='customer-statement')
]