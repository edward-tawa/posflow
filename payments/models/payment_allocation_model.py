from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger
import uuid



class PaymentAllocation(CreateUpdateBaseModel):
    PREFIX = 'PA'
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='payment_allocations'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='payment_allocations'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    allocated_to_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    allocated_to_object_id = models.PositiveIntegerField()
    allocated_to = GenericForeignKey('allocated_to_content_type', 'allocated_to_object_id')
    allocation_number = models.CharField(max_length=20, unique=True, editable=False)
    allocation_date = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='payment_allocations')
    total_amount_allocated = models.DecimalField(max_digits=12, decimal_places=2)

    def generate_allocation_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated PaymentAllocation number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate allocation number if not provided
        if not self.allocation_number:
            self.allocation_number = self.generate_allocation_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.allocation_number} - {self.amount_allocated}"

    class Meta:
        ordering = ['-allocation_date']
        verbose_name = "Payment Allocation"
        verbose_name_plural = "Payment Allocations"