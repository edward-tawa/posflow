from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'

    def ready(self):
        import customers.signals.customer_activity_logs_signal
        import customers.signals.customer_branch_history_activity_logs_signal