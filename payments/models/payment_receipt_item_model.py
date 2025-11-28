from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger
import uuid


class PaymentReceiptItem(CreateUpdateBaseModel):
    payment_receipt = models.ForeignKey(
        'payments.PaymentReceipt',
        on_delete=models.CASCADE,
        related_name='items'
    )
    description = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return (self.subtotal * (self.tax_rate / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def total_price(self):
        return (self.subtotal + self.tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.description} (x{self.quantity}) - {self.total_price}"
    
    class Meta:
        indexes = [
            models.Index(fields=['payment_receipt']),
        ]