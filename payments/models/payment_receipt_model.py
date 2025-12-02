from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from loguru import logger
import uuid



class PaymentReceipt(CreateUpdateBaseModel):
    PREFIX = 'PR'
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='payment_receipts'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='payment_receipts'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='receipts'
    )
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    receipt_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_payment_receipts'
    )
    def generate_receipt_number(self):
        """ Generate a unique receipt number. """
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated PaymentReceipt number: {number}")
        return number

    def update_amount_received(self):
        """Recalculate and update the amount based on related items."""
        # total_received = self.items.aggregate(total=Sum('total_price'))['total'] or 0

        # if self.amount != total_received:
        #     self.amount = total_received
        #     super().save(update_fields=['amount'])
        pass


    def save(self, *args, **kwargs):
        # Auto-generate receipt number if not provided
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()

        super().save(*args, **kwargs)

        # **Important: update amount after save**
        self.update_amount_received()


    def __str__(self):
        return f"{self.receipt_number} - {self.amount}"

    class Meta:
        ordering = ['-receipt_date']
        verbose_name = "Payment Receipt"
        verbose_name_plural = "Payment Receipts"
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['receipt_date']),
        ]