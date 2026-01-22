from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger
import uuid



class Payment(CreateUpdateBaseModel):
    PREFIX = 'PAY'
    PAYMENT_TYPE = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
        ]
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    paid_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_made'
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE, default='incoming')
    payment_number = models.CharField(max_length=20, unique=True, editable=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='payments')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=50)
    reference_model = models.CharField(max_length=50, null=True, blank=True) # reference the model that triggered the payment
    reference_id = models.PositiveIntegerField(null=True, blank=True)

    def generate_payment_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated Payment number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate payment number if not provided
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_number} - {self.amount}"

    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"