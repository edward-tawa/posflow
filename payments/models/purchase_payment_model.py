from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel



class PurchasePayment(CreateUpdateBaseModel):
    # Purchase payment mode

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='purchase_payments')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='purchase_payments')
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, related_name='purchase_payments')
    payment_method = models.ForeignKey('payments.PaymentMethod', on_delete=models.CASCADE, related_name='purchase_payments')
    purchase_order = models.ForeignKey('suppliers.PurchaseOrder', on_delete=models.CASCADE, related_name='purchase_payments', null=True, blank=True)
    purchase = models.ForeignKey('suppliers.Purchase', on_delete=models.CASCADE, related_name='purchase_payments', null=True, blank=True)
    purchase_invoice = models.ForeignKey('suppliers.PurchaseInvoice', on_delete=models.CASCADE, related_name='purchase_payments', null=True, blank=True)
    issued_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='issued_purchase_payments')    



    class Meta:
        models.Index(fields=['payment', 'purchase_order', 'purchase_invoice'])
        models.Index(fields=['company', 'branch'])
        models.Index(fields=['issued_by'])

        models.UniqueConstraint(fields=['payment', 'purchase_order'], name='unique_payment_purchase_order')
        models.UniqueConstraint(fields=['payment', 'purchase_invoice'], name='unique_payment_purchase_invoice')
    
    def __str__(self):
        return f"Payment {self.id} for Purchase Order {self.purchase_order.id}"
    
