from rest_framework.routers import DefaultRouter
from accounts.views.account_views import AccountViewSet



router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
urlpatterns = router.urls