from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_order_views import PurchaseOrderViewSet


router = DefaultRouter()
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')

urlpatterns = router.urls