from django.urls import path
from rest_framework.routers import DefaultRouter
from customers.views.create_credit_sale_views import CreateCreditSaleView


urlpatterns = [
    path('customers/<int:customer_id>/create-credit-sale', CreateCreditSaleView.as_view(), name='create-credit-sale')
]