from rest_framework.routers import DefaultRouter
from employees.views.remuneration_views import RemunerationViewSet

router = DefaultRouter()
router.register(r'remunerations', RemunerationViewSet, basename='remuneration')
urlpatterns = router.urls