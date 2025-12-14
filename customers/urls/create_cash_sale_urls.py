from rest_framework.routers import DefaultRouter
from customers.views.create_cash_sale_views import CreateCashSaleView


router = DefaultRouter()
router.register(r'customers/(?P<customer_id>\d+)/create-cash-sale', CreateCashSaleView, basename='create-cash-sale')
urlpatterns = router.urls