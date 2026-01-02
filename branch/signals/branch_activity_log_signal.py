# branch/signals/branch_activity_logs_signal.py
from branch.models.branch_model import Branch
from config.activity_log.crud_registry import register_crud_signals

register_crud_signals(
    Branch,
    actions={
        'create': 'branch_created',
        'update': 'branch_updated',
        'delete': 'branch_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Branch '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'branch_id': instance.id,
        'branch_name': instance.name,
        'created': created,
    }
)

