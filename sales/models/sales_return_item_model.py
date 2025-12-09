from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger


class SalesReturnItem(CreateUpdateBaseModel):
    sales_return = models.ForeignKey('sales.SalesReturn', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='sales_return_items')
    product_name = models.CharField(max_length=100)
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

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        if not (0 <= self.tax_rate <= 100):
            raise ValidationError("Tax rate must be between 0 and 100.")

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"
    
    class Meta:
        indexes = [
            models.Index(fields=['sales_return']),
            models.Index(fields=['product']),
        ]
