from django.apps import AppConfig


class BranchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'branch'

    def ready(self):
        import branch.signals.branch_activity_log_signal