from inventory.views.stock_adjustment_views import StockAdjustmentViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'stock-adjustment', StockAdjustmentViewSet, basename='stock-adjustment')
urlpatterns = router.urls