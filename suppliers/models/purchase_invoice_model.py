from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid



class PurchaseInvoice(CreateUpdateBaseModel):
    PREFIX = 'PurInv'
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='purchase_invoices'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='purchase_invoices'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='purchase_invoices'
    )
    purchase_order = models.ForeignKey(
        'suppliers.PurchaseOrder',
        on_delete=models.CASCADE,
        related_name='purchase_invoices',
        null=True,
        blank=True
    )
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    invoice_date = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_purchase_invoices'
    )

    def generate_invoice_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated PurchaseInvoice number: {number}")
        return number
    

    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not provided
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
        # Update total amount based on items
        self.update_total_amount()

    def update_total_amount(self):
        total = sum(item.total_price for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.invoice_number} - {self.total_amount}"

    class Meta:
        ordering = ['-invoice_date']
        verbose_name = "Purchase Invoice"
        verbose_name_plural = "Purchase Invoices"