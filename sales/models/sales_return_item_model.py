from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger


class SalesReturnItem(CreateUpdateBaseModel):
    sales_receipt = models.ForeignKey(
        'sales.SalesReceipt',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # self.receipt.update_total_amount()

    def delete(self, *args, **kwargs):
        receipt = self.receipt
        super().delete(*args, **kwargs)
        receipt.update_total_amount()

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
