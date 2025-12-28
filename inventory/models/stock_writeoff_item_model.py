from django.db import models
from inventory.models.stock_writeoff_model import StockWriteOff
from config.models.create_update_base_model import CreateUpdateBaseModel


class StockWriteOffItem(CreateUpdateBaseModel):
    write_off = models.ForeignKey(
        StockWriteOff,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4
    )

    class Meta:
        unique_together = ("write_off", "product")
        indexes = [
            models.Index(fields=["write_off", "product"]),
        ]

    def __str__(self):
        return f"Item {self.product} - Qty: {self.quantity} for Write-Off {self.write_off.reference}"
