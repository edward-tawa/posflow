# suppliers/signals/supplier_credit_note_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_credit_note_item_model import SupplierCreditNoteItem

register_crud_signals(
    SupplierCreditNoteItem,
    actions={
        'create': 'supplier_credit_note_item_created',
        'update': 'supplier_credit_note_item_updated',
        'delete': 'supplier_credit_note_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SupplierCreditNoteItem '{instance.name if instance.name else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_credit_note_item_id': instance.id,
        'supplier_credit_note_item_name': instance.name if instance.name else None,
        'created': created,
    }
)