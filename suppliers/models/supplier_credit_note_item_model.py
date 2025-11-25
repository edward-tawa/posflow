from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid





class SupplierCreditNoteItem(CreateUpdateBaseModel):
    supplier_credit_note = models.ForeignKey(
        'suppliers.SupplierCreditNote',
        on_delete=models.CASCADE,
        related_name='items'
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total_price(self):
        total = self.quantity * self.unit_price
        logger.info(f"Calculated total price for item {self.id}: {total}")
        return total

    def __str__(self):
        return f"Item {self.id} - {self.description}"

    class Meta:
        ordering = ['id']
        verbose_name = "Supplier Credit Note Item"
        verbose_name_plural = "Supplier Credit Note Items"