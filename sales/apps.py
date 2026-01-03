from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sales'


    def ready(self):
        import sales.signals.sales_order_activity_logs_signal
        import sales.signals.sales_payment_activity_logs_signal
        import sales.signals.sales_return_activity_logs_signal
        import sales.signals.sales_return_item_activity_logs_signal
        import sales.signals.sales_quotation_item_activity_logs_signal
        import sales.signals.sales_quotation_activity_logs_signal
        import sales.signals.sales_invoice_activity_logs_signal
        import sales.signals.sales_invoice_item_activity_logs_signal
        import sales.signals.sales_receipt_activity_logs_signal
        import sales.signals.sales_receipt_item_activity_logs_signal
        import sales.signals.delivery_note_activity_logs_signal
        import sales.signals.delivery_note_item_activity_logs_signal
        import sales.signals.sales_order_activity_logs_signal
        import sales.signals.sales_order_item_activity_logs_signal
        
