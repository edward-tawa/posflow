# sales/signals/sales_invoice_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_invoice_model import SalesInvoice


register_crud_signals(
    SalesInvoice,
    actions={
        'create': 'sales_invoice_created',
        'update': 'sales_invoice_updated',
        'delete': 'sales_invoice_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesInvoice '{instance.invoice_number}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_invoice_id': instance.id,
        'sales_invoice_number': instance.invoice_number,
        'created': created,
    }
)