from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid
from django.core.exceptions import ValidationError
from django.db.models import F, Sum, FloatField


class Transfer(CreateUpdateBaseModel):
    PREFIX = "TR"
    TYPE_CHOICES = (
        ("cash", "Cash Transfer"),
        ("product", "Product Transfer"),
    )

    
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='transfers')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='transfers')
    reference_number = models.CharField(max_length=100, unique=True)
    transferred_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_made')
    received_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_received')
    sent_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_sent')
    transfer_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('on_going', 'Ongoing'),
            ('on_hold', 'On Hold'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )

    def update_total_amount(self):
        """
        Automatically update total_amount based on the type of transfer.
        """
        if self.type == "product" and hasattr(self, "product_transfer") and self.product_transfer:
            # sum up all items
            total = self.items.aggregate(
                total_amount=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
            ).get('total_amount') or 0
            self.total_amount = total
            self.save(update_fields=['total_amount'])

        elif self.type == "cash" and hasattr(self, "cash_transfer") and self.cash_transfer:
            self.total_amount = self.cash_transfer.total_amount
            self.save(update_fields=['total_amount'])


    class Meta:
        unique_together = ('company', 'reference_number')
        ordering = ['-transfer_date', 'id']

    def generate_reference_number(self):
        unique_code = uuid.uuid4().hex[:6].upper()
        logger.info(f"Unique code for Transfer: {unique_code} successfully generated.")
        return f"{self.PREFIX}-{unique_code}"


    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
        logger.bind(reference=self.reference_number).info(f"Transfer {self.reference_number} saved to database successfully.")

    def __str__(self):
        return f"Transfer {self.reference_number} ({self.company.name})"
