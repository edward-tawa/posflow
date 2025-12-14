from django.db import models, transaction
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger


class SalesReturnItem(CreateUpdateBaseModel):
    """
    Model representing an item within a Sales Return.
    Handles subtotal, tax, and total price calculations.
    Includes status tracking (Pending, Processed/Accepted, Cancelled/Rejected).
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSED', 'Processed/Accepted'),
        ('CANCELLED', 'Cancelled/Rejected'),
    ]

    sales_return = models.ForeignKey(
        'sales.SalesReturn',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='sales_return_items'
    )
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    @property
    def subtotal(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def tax_amount(self) -> Decimal:
        return (self.subtotal * (self.tax_rate / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def total_price(self) -> Decimal:
        return (self.subtotal + self.tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def clean(self):
        """Validates quantity, unit price, and tax rate."""
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        if not (0 <= self.tax_rate <= 100):
            raise ValidationError("Tax rate must be between 0 and 100.")
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {self.status}")

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Override save to ensure total updates on the parent sales return."""
        super().save(*args, **kwargs)
        if self.sales_return:
            self.sales_return.update_total_amount()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """Override delete to update total on parent sales return."""
        sales_return = self.sales_return
        super().delete(*args, **kwargs)
        if sales_return:
            sales_return.update_total_amount()
            logger.info(
                f"Deleted SalesReturnItem '{self.product_name}' and updated total for return '{sales_return.return_number}'."
            )

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price} [{self.status}]"

    class Meta:
        indexes = [
            models.Index(fields=['sales_return']),
            models.Index(fields=['product']),
        ]
        ordering = ['sales_return', 'id']
