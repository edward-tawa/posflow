from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from loguru import logger
import uuid



class Transaction(CreateUpdateBaseModel):
    TRANSACTION_TYPES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('SALES RETURN', 'Sales Return'),
        ('PURCHASE RETURN', 'Purchase Return'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_number = models.CharField(max_length=20, unique=True, editable=False)
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def generate_transaction_number(self):
        number = f"TRX-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated Transaction number: {number}")
        return number

    def update_total_amount(self):
        total = self.items.aggregate(total=Sum('total_price'))['total'] or 0
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])


    def save(self, *args, **kwargs):
        # Auto-generate transaction number if not provided
        if not self.transaction_number:
            self.transaction_number = self.generate_transaction_number()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.transaction_number} - {self.transaction_type} - {self.total_amount}"
    

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['transaction_number']),
        ]