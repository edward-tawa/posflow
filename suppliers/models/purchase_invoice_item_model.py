from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid

class PurchaseInvoiceItem(CreateUpdateBaseModel):
    purchase_invoice = models.ForeignKey(
        'suppliers.PurchaseInvoice',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='purchase_invoice_items'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    @property
    def tax_amount(self):
        tax_rate = self.product.tax_rate or 0
        return (self.total_price * tax_rate) / 100
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def total_price(self):
        return self.subtotal + self.tax_amount
    

    def save(self, *args, **kwargs):
        self.total_price = self.subtotal
        super().save(*args, **kwargs)
        # Update the total amount of the related purchase invoice
        self.purchase_invoice.update_total_amount()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} @ {self.unit_price}"

    class Meta:
        verbose_name = "Purchase Invoice Item"
        verbose_name_plural = "Purchase Invoice Items"