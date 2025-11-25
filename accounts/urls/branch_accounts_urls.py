from rest_framework.routers import DefaultRouter
from accounts.views.branch_account_views import BranchAccountViewSet


router = DefaultRouter()
router.register(r'branch-accounts', BranchAccountViewSet, basename='branch-account')
urlpatterns = router.urls