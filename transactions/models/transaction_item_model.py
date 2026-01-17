from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
from decimal import Decimal, ROUND_HALF_UP

from transactions.models.transaction_model import Transaction



class TransactionItem(CreateUpdateBaseModel):
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='transaction_items'
    )
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return (self.subtotal * (self.tax_rate / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        if not (0 <= self.tax_rate <= 100):
            raise ValidationError("Tax rate must be between 0 and 100.")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Validate before saving
        self.total_price = (self.subtotal + self.tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        transaction: Transaction = self.transaction
        super().delete(*args, **kwargs)
        transaction.update_total_amount()

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.unit_price}"
    
    class Meta:
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['product']),
        ]