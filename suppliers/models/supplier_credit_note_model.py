from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid



class SupplierCreditNote(CreateUpdateBaseModel):
    PREFIX = 'SCN'
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='supplier_credit_notes'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='credit_notes'
    )
    credit_note_number = models.CharField(max_length=20, unique=True, editable=False)
    credit_date = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_supplier_credit_notes'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def generate_credit_note_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated SupplierCreditNote number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate credit note number if not provided
        if not self.credit_note_number:
            self.credit_note_number = self.generate_credit_note_number()
        super().save(*args, **kwargs)
        # Update total amount based on items
        self.update_total_amount()

    def update_total_amount(self):
        total = sum(item.total_price for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.credit_note_number} - {self.total_amount}"

    class Meta:
        ordering = ['-credit_date']
        verbose_name = "Supplier Credit Note"
        verbose_name_plural = "Supplier Credit Notes"