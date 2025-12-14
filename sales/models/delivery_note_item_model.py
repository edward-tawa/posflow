from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class DeliveryNoteItem(CreateUpdateBaseModel):
    delivery_note = models.ForeignKey('sales.DeliveryNote', on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='delivery_note_items')
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total_price(self):
        return self.subtotal + self.tax_amount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delivery_note:
            self.delivery_note.update_total_amount()

    def delete(self, *args, **kwargs):
        note = self.delivery_note
        super().delete(*args, **kwargs)
        if note:
            note.update_total_amount()
            logger.info(f"Deleted DeliveryNoteItem '{self.product_name}' and updated total for note '{note.delivery_number}'.")

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"

    class Meta:
        indexes = [
            models.Index(fields=['delivery_note']),
            models.Index(fields=['product']),
        ]
