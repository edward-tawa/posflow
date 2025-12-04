from django.db import models
from django.forms import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from loguru import logger
import uuid


class Transaction(CreateUpdateBaseModel):
    TRANSACTION_CATEGORIES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('SALES RETURN', 'Sales Return'),
        ('PURCHASE RETURN', 'Purchase Return'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TRANSFER', 'Transfer'),
    ]

    TRANSACTION_TYPES = [
        ('INCOMING', 'Incoming'),
        ('OUTGOING', 'Outgoing'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('VOIDED', 'Voided'),
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

    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True
    )

    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True
    )

    debit_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='debit_transactions'
    )

    credit_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='credit_transactions'
    )
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_category = models.CharField(max_length=20, choices=TRANSACTION_CATEGORIES)
    transaction_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
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
    
    def clean(self):
        """
        Validates that total_amount is non-negative.
        """
        if self.total_amount < Decimal('0.00'):
            logger.error(f"Transaction {self.transaction_number} has negative total amount: {self.total_amount}")
            raise ValidationError("Total amount cannot be negative.")
        if self.pk:
            previous = Transaction.objects.get(pk=self.pk)
            # Example rule: VOIDED transactions cannot be changed back
            if previous.status == 'VOIDED' and self.status != 'VOIDED':
                raise ValidationError("Cannot change the status of a VOIDED transaction.")
            
            # Example rule: COMPLETED transactions cannot go back to PENDING
            if previous.status == 'COMPLETED' and self.status in ['PENDING', 'DRAFT']:
                raise ValidationError("Cannot move a COMPLETED transaction back to PENDING or DRAFT.")

    def save(self, *args, **kwargs):
        # Auto-generate transaction number if not provided
        if not self.transaction_number:
            self.transaction_number = self.generate_transaction_number()
        self.full_clean()  # clean method to enforce validations
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.transaction_number} - {self.transaction_type} - {self.total_amount} ({self.status})"

    

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['transaction_number']),
            models.Index(fields=['status']),
        ]