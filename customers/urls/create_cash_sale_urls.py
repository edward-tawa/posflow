from django.urls import path
from rest_framework.routers import DefaultRouter
from customers.views.create_cash_sale_views import CreateCashSaleView


urlpatterns = [
    path(
        "customers/<int:customer_id>/create-cash-sale/",
        CreateCashSaleView.as_view(),
        name="create-cash-sale"
    ),
]