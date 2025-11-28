from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger
import uuid


class Refund(CreateUpdateBaseModel):
    PREFIX = 'RFND'
    REASON_CHOICES = [
        ('product_defect', 'Product Defect'),
        ('wrong_item', 'Wrong Item Sent'),
        ('customer_request', 'Customer Request'),
        ('other', 'Other')
        ]
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    refund_number = models.CharField(max_length=20, unique=True, editable=False)
    refund_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default='customer_request')
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_refunds'
    )
    notes = models.TextField(blank=True, null=True)
   

    def generate_refund_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated Refund number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate refund number if not provided
        if not self.refund_number:
            self.refund_number = self.generate_refund_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.refund_number} - {self.amount}"

    class Meta:
        ordering = ['-refund_date']
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"


        indexes = [
            models.Index(fields=['refund_number']),
            models.Index(fields=['refund_date']),
        ]