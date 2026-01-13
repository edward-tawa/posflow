from rest_framework.routers import DefaultRouter
from currency.views.currency_views import CurrencyViewSet

router = DefaultRouter()
router.register(r'currency', CurrencyViewSet, basename='currency')
urlpatterns = router.urls