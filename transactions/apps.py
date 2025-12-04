from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'


    def ready(self):
            # Import signal handlers to ensure they are registered
        import transactions.signals.apply_transaction_signal
