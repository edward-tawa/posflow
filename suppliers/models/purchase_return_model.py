from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid

class PurchaseReturn(CreateUpdateBaseModel):
    PREFIX = 'PR'
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='purchase_returns'
    )
    
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='purchase_returns'
    )

    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='purchase_returns',
        null=True,
        blank=True
    )

    purchase_order = models.ForeignKey(
        'suppliers.PurchaseOrder',
        on_delete=models.CASCADE,
        related_name='purchase_returns'
    )

    purchase = models.ForeignKey(
        'suppliers.Purchase',
        on_delete=models.CASCADE,
        related_name='purchase_returns',
        null=True,
        blank=True
    )

    purchase_return_number = models.CharField(max_length=20, unique=True, editable=False)
    return_date = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_purchase_returns'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def generate_purchase_return_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated PurchaseReturn number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate purchase return number if not provided
        if not self.purchase_return_number:
            self.purchase_return_number = self.generate_purchase_return_number()
        super().save(*args, **kwargs)
        # Update total amount based on items
        self.update_total_amount()

    def update_total_amount(self):
        total = sum(item.total_price for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.purchase_return_number} - {self.total_amount}"

    class Meta:
        ordering = ['-return_date']
        verbose_name = "Purchase Return"
        verbose_name_plural = "Purchase Returns"


