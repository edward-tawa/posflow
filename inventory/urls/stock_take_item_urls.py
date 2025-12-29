from rest_framework.routers import DefaultRouter
from inventory.views.stock_take_item_views import StockTakeItemViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'stocktake-item', StockTakeItemViewSet, basename='stocktake-item')
urlpatterns = router.urls