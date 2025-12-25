from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class PurchaseItem(CreateUpdateBaseModel):
    purchase = models.ForeignKey(
        'suppliers.Purchase',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='purchase_items'
    )
    purchase_order_item = models.ForeignKey(
        'suppliers.PurchaseOrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_items'
    )
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )  # percentage

    # -------------------------
    # CALCULATED FIELDS
    # -------------------------
    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / 100)

    @property
    def total_price(self):
        return self.subtotal + self.tax_amount

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"

    class Meta:
        indexes = [
            models.Index(fields=['purchase']),
            models.Index(fields=['product']),
        ]
