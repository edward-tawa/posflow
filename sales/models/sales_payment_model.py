# from django.db import models, transaction
# from django.core.exceptions import ValidationError
# from config.models.create_update_base_model import CreateUpdateBaseModel
# from loguru import logger
# import uuid


# class SalesPayment(CreateUpdateBaseModel):
#     """
#     Docstring for SalesPayment
#         Model representing the application of a payment to a sales order and receipt.
#     """
#     sales_order = models.ForeignKey(
#         'sales.SalesOrder', on_delete=models.CASCADE, related_name='payments'
#     )

#     sale = models.ForeignKey(
#         'sales.Sale', on_delete=models.CASCADE, related_name='payments'
#     )

#     sales_receipt = models.ForeignKey(
#         'sales.SalesReceipt', on_delete=models.CASCADE, related_name='payments', null=True, blank=True
#     )

#     payment = models.ForeignKey(
#         'payments.Payment', on_delete=models.CASCADE, related_name='sales_payments'
#     )

#     currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='sales_payments')

#     amount_applied = models.DecimalField(max_digits=12, decimal_places=2)


#     def clean(self):
#         if self.amount_applied > self.payment.amount:
#             raise ValidationError("Applied amount cannot exceed payment amount")
        
#     def __str__(self):
#         return f"Payment {self.payment.payment_number} applied to Sales Order {self.sales_order.order_number} - Amount: {self.amount_applied}"
    
#     def save(self, *args, **kwargs):
#         self.full_clean()  # run validations
#         super().save(*args, **kwargs)

#     class Meta:
#         indexes = [
#             models.Index(fields=['sales_order']),
#             models.Index(fields=['sales_receipt']),
#             models.Index(fields=['payment']),
#         ]