# sales/signals/sales_quotation_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_quotation_model import SalesQuotation


register_crud_signals(
    SalesQuotation,
    actions={
        'create': 'sales_quotation_created',
        'update': 'sales_quotation_updated',
        'delete': 'sales_quotation_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesQuotation '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_quotation_id': instance.id,
        'sales_quotation_name': instance.name if instance.name else None,
        'created': created,
    }
)