from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class PurchasePayment(CreateUpdateBaseModel):
    PREFIX = 'PP'

    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        CARD = 'card', 'Card'
        ECOCASH = 'ecocash', 'EcoCash'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        LAYBY = 'layby', 'Layby'
        PAYLATER = 'paylater', 'PayLater'

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='purchase_payments'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='purchase_payments'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='purchase_payments'
    )
    purchase_payment_number = models.CharField(max_length=20, unique=True, editable=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.CASH
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_purchase_payments'
    )

    def generate_purchase_payment_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated PurchasePayment number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate purchase payment number if not provided
        if not self.purchase_payment_number:
            self.purchase_payment_number = self.generate_purchase_payment_number()
        super().save(*args, **kwargs)
        # Update total amount based on items
        self.update_total_amount()

    def update_total_amount(self):
        total = sum(item.total_price for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.purchase_payment_number} - {self.total_amount}"

    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Purchase Payment"
        verbose_name_plural = "Purchase Payments"