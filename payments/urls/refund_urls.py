from rest_framework.routers import DefaultRouter
from payments.views.refund_views import RefundViewSet


router = DefaultRouter()
router.register(r'refunds', RefundViewSet, basename='refund')
urlpatterns = router.urls