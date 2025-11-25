from rest_framework.routers import DefaultRouter
from inventory.views.stock_movement_views import StockMovementViewSet


router = DefaultRouter()
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')
urlpatterns = router.urls