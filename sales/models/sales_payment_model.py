from django.db import models, transaction
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class SalesPayment(CreateUpdateBaseModel):
    PREFIX = 'SP'

    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        CARD = 'card', 'Card'
        ECOCASH = 'ecocash', 'EcoCash'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        LAYBY = 'layby', 'Layby'
        PAYLATER = 'paylater', 'PayLater'

    company = models.ForeignKey(
        'company.Company', on_delete=models.CASCADE, related_name='sales_payments'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.CASCADE, related_name='sales_payments'
    )
    sales_order = models.ForeignKey(
        'sales.SalesOrder', on_delete=models.CASCADE, related_name='payments'
    )
    payment_number = models.CharField(max_length=20, unique=True)
    payment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.CASH
    )
    processed_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='processed_sales_payments'
    )
    notes = models.TextField(blank=True, null=True)

    def generate_payment_number(self):
        """Generates a unique payment number for the sales payment."""
        return f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"

    def clean(self):
        """Validates payment data."""
        if self.amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")
        if self.payment_method not in dict(self.Method.choices):
            raise ValidationError(f"Invalid payment method: {self.payment_method}")

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)

        # Update order status based on total payments
        total_paid = sum(p.amount for p in self.sales_order.payments.all())
        if total_paid >= self.sales_order.total_amount:
            self.sales_order.status = 'PAID'
            self.sales_order.save(update_fields=['status'])

    def __str__(self):
        return f"Payment {self.payment_number} - Order {self.sales_order.order_number}"

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "payment_date"]),
            models.Index(fields=["sales_order"]),
            models.Index(fields=["processed_by"]),
            models.Index(fields=["sales_order", "payment_date"]),
        ]
