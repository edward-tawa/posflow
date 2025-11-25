from rest_framework.routers import DefaultRouter
from transfers.views.product_transfer_item_view import ProductTransferItemViewSet

router = DefaultRouter()
router.register(r'product-transfer-items', ProductTransferItemViewSet, basename='product-transfer-item')

urlpatterns = router.urls