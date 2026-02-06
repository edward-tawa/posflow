# from django.db import models
# from django.forms import ValidationError
# from config.models.create_update_base_model import CreateUpdateBaseModel
# from loguru import logger
# import uuid



# class PurchasePayment(CreateUpdateBaseModel):
#     supplier = models.ForeignKey(
#         'suppliers.Supplier',
#         on_delete=models.CASCADE,
#         related_name='purchase_payments'
#     )

#     payment = models.ForeignKey(
#         'payments.Payment',
#         on_delete=models.CASCADE,
#         related_name='purchase_payments'
#     )
    
#     purchase_invoice = models.ForeignKey(
#         'suppliers.PurchaseInvoice',
#         on_delete=models.CASCADE,
#         related_name='purchase_payments'
#     )
#     currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='purchase_payments')
#     total_amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
#     payment_date = models.DateField(auto_now_add=True)

#     def clean(self):
#         if self.total_amount_paid < 0:
#             raise ValidationError("Amount paid cannot be negative")
#         if self.total_amount_paid > self.payment.amount:
#             raise ValidationError("Amount paid cannot exceed payment amount")
    
#     def save(self, *args, **kwargs):
#         self.full_clean()  # run validations
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Payment {self.payment.payment_number} for Supplier {self.supplier.name} - Amount: {self.total_amount_paid}"

#     class Meta:
#         ordering = ['-payment_date']
#         indexes = [
#             models.Index(fields=['supplier']),
#             models.Index(fields=['payment']),
#         ]
