from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_return_item_views import PurchaseReturnItemViewSet

router = DefaultRouter()
router.register(r'purchase-return-items', PurchaseReturnItemViewSet, basename='purchase-return-item')
urlpatterns = router.urls