from rest_framework.routers import DefaultRouter
from transfers.views.product_transfer_view import ProductTransferViewSet



router = DefaultRouter()
router.register(r'product-transfers', ProductTransferViewSet, basename='product-transfer')

urlpatterns = router.urls