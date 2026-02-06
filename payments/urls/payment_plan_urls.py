from payments.views.payment_plan_views import PaymentPlanViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'payment-plan', PaymentPlanViewSet, basename='payment-plan')
urlpatterns = router.urls