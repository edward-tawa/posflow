# suppliers/signals/supplier_credit_note_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_credit_note_model import SupplierCreditNote

register_crud_signals(
    SupplierCreditNote,
    actions={
        'create': 'supplier_credit_note_created',
        'update': 'supplier_credit_note_updated',
        'delete': 'supplier_credit_note_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SupplierCreditNote '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_credit_note_id': instance.id,
        'supplier_credit_note_name': instance.name,
        'created': created,
    }
)