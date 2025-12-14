from django.db import models, transaction
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class DeliveryNote(CreateUpdateBaseModel):
    PREFIX = "DN"

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    company = models.ForeignKey(
        'company.Company', on_delete=models.CASCADE, related_name='delivery_notes'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.CASCADE, related_name='delivery_notes'
    )
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE, related_name='delivery_notes'
    )
    sales_order = models.ForeignKey(
        'sales.SalesOrder', on_delete=models.CASCADE, related_name='delivery_notes'
    )
    delivery_number = models.CharField(max_length=20, unique=True)
    delivery_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issued_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='issued_delivery_notes'
    )
    notes = models.TextField(blank=True, null=True)

    def generate_delivery_number(self):
        """Generates a unique delivery number."""
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Generated delivery number successfully: {number}")
        return number

    @transaction.atomic
    def update_total_amount(self):
        """Update total amount from related delivery items."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        logger.info(f"Updated total amount for delivery note {self.delivery_number}: {total}")
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        if not self.delivery_number:
            self.delivery_number = self.generate_delivery_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Delivery Note {self.delivery_number} - {self.customer.name}"

    class Meta:
        indexes = [
            models.Index(fields=['delivery_number']),
            models.Index(fields=['issued_by']),
            models.Index(fields=['status']),
        ]