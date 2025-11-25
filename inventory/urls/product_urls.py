from rest_framework.routers import DefaultRouter
from inventory.views.product_views import ProductViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = router.urls
