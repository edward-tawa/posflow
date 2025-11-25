from rest_framework.routers import DefaultRouter
from sales.views.delivery_note_views import DeliveryNoteViewSet



router = DefaultRouter()
router.register(r'delivery-notes', DeliveryNoteViewSet, basename='delivery-note')
urlpatterns = router.urls