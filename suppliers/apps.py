from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suppliers'


    def ready(self):
        import suppliers.signals.purchase_activity_logs_signal
        import suppliers.signals.supplier_credit_note_activity_logs_signal
        import suppliers.signals.supplier_receipt_activity_logs_signal
        import suppliers.signals.supplier_receipt_item_activity_logs_signal
        import suppliers.signals.supplier_debit_note_activity_logs_signal
        import suppliers.signals.supplier_debit_note_item_activity_logs_signal
        import suppliers.signals.supplier_credit_note_item_activity_logs_signal
        import suppliers.signals.supplier_activity_logs_signal
        import suppliers.signals.purchase_activity_logs_signal
        import suppliers.signals.purchase_order_activity_logs_signal
        import suppliers.signals.purchase_order_item_activity_logs_signal
        import suppliers.signals.purchase_return_activity_logs_signal
        import suppliers.signals.purchase_return_item_activity_logs_signal
        import suppliers.signals.purchase_item_activity_logs_signal
        import suppliers.signals.purchase_invoice_activity_logs_signal
        import suppliers.signals.purchase_invoice_item_activity_logs_signal