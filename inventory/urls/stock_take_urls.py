from rest_framework.routers import DefaultRouter
from inventory.views.stock_take_views import StockTakeViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'stock-takes', StockTakeViewSet, basename='stock-take')
urlpatterns = router.urls
