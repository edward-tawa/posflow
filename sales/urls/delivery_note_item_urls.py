from rest_framework.routers import DefaultRouter
from sales.views.delivery_note_item_views import DeliveryNoteItemViewSet

router = DefaultRouter()
router.register(r'delivery-note-items', DeliveryNoteItemViewSet, basename='delivery-note-item')
urlpatterns = router.urls