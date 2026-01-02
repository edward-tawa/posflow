from django.apps import AppConfig


class TransfersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transfers'


    def ready(self):
        import transfers.signals.transfer_activity_logs_signal  
        import transfers.signals.cash_transfer_activity_logs_signal
        import transfers.signals.product_transfer_item_activity_logs_signal
        import transfers.signals.product_transfer_activity_logs_signal
        