from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid
from decimal import Decimal


class PurchaseReturnItem(CreateUpdateBaseModel):
    purchase_return = models.ForeignKey(
        'suppliers.PurchaseReturn',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='purchase_return_items'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage

    @property
    def subtotal(self):
        return Decimal(self.quantity * self.unit_price)

    @property
    def tax_amount(self):
        return self.subtotal * Decimal(self.tax_rate / 100)

    @property
    def total_price(self):
        return self.subtotal + self.tax_amount

    class Meta:
        indexes = [
            models.Index(fields=['purchase_return']),
            models.Index(fields=['product']),
        ]
        verbose_name = "Purchase Return Item"
        verbose_name_plural = "Purchase Return Items"

    def __str__(self):
        return f"{self.product.name} x{self.quantity} (Total: {self.total_price})"
