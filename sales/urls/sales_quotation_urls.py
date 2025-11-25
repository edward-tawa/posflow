from rest_framework.routers import DefaultRouter
from sales.views.sales_quotation_views import SalesQuotationViewSet




router = DefaultRouter()
router.register(r'sales-quotations', SalesQuotationViewSet, basename='sales-quotation')
urlpatterns = router.urls