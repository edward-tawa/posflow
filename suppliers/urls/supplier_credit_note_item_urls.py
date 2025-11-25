from rest_framework.routers import DefaultRouter
from suppliers.views.supplier_credit_note_item_views import SupplierCreditNoteItemViewSet


router = DefaultRouter()
router.register(r'supplier-credit-note-items', SupplierCreditNoteItemViewSet, basename='supplier-credit-note-item')
urlpatterns = router.urls