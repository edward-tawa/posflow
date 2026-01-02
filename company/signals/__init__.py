# company/signals/company_activity_logs_signal.py
from company.models.company_model import Company
from config.activity_log.crud_registry import register_crud_signals

register_crud_signals(
    Company,
    actions={
        'create': 'company_created',
        'update': 'company_updated',
        'delete': 'company_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Company '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'company_id': instance.id,
        'company_name': instance.name,
        'created': created,
    }
)

