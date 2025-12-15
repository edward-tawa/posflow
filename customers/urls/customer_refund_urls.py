from django.urls import path
from rest_framework.routers import DefaultRouter
from customers.views.customer_refund_views import CustomerRefundView


urlpatterns = [
    path('customers/<int:customer_id>/refund', CustomerRefundView.as_view(), name='customer-refund')
]