from rest_framework.routers import DefaultRouter
from inventory.views.product_category_views import ProductCategoryViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'product-categories', ProductCategoryViewSet, basename='product-category')

urlpatterns = router.urls