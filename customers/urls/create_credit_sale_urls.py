from rest_framework.routers import DefaultRouter
from customers.views.create_credit_sale_views import CreateCreditSaleView

router = DefaultRouter()
router.register(r'customers/(?P<customer_id>\d+)/create-credit-sale', CreateCreditSaleView, basename='create-credit-sale')
urlpatterns = router.urls