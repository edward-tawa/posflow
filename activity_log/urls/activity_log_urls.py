from rest_framework.routers import DefaultRouter
from activity_log.views.activity_log_views import ActivityLogViewSet



router = DefaultRouter()
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')
urlpatterns = router.urls