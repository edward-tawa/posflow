from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_order_item_views import PurchaseOrderItemViewSet

router = DefaultRouter()
router.register(r'purchase-order-items', PurchaseOrderItemViewSet, basename='purchaseorderitem')

urlpatterns = router.urls