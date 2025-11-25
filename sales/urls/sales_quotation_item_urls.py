from rest_framework.routers import DefaultRouter
from sales.views.sales_quotation_item_views import SalesQuotationItemViewSet



router = DefaultRouter()
router.register(r'sales-quotation-items', SalesQuotationItemViewSet, basename='sales-quotation-item')
urlpatterns = router.urls