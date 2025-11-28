from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from django.core.exceptions import ValidationError
from loguru import logger
import uuid

# will not be used to track allocations. its being done in the purchase payment model directly. unless we need detailed allocation records.

class PurchasePaymentAllocation(CreateUpdateBaseModel):
    PREFIX = 'PPA'

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='purchase_payment_allocations'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='purchase_payment_allocations'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='purchase_payment_allocations'
    )
    purchase_payment = models.ForeignKey(
        'suppliers.PurchasePayment',
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    purchase_invoice = models.ForeignKey(
        'suppliers.PurchaseInvoice',
        on_delete=models.CASCADE,
        related_name='payment_allocations'
    )
    allocation_number = models.CharField(max_length=20, unique=True, editable=False)
    allocation_date = models.DateTimeField(auto_now_add=True)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allocated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='allocated_purchase_payments'
    )

    def generate_allocation_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated PurchasePaymentAllocation number: {number}")
        return number
    
    def clean(self):

        if self.allocated_amount <= 0:
            raise ValidationError("Allocated amount must be greater than zero.")

        if self.purchase_invoice.balance < self.allocated_amount:
            raise ValidationError("Allocated amount cannot exceed invoice balance.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.allocation_number:
            self.allocation_number = self.generate_allocation_number()

        super().save(*args, **kwargs)

        if is_new:
            invoice = self.purchase_invoice
            invoice.total_amount -= self.allocated_amount
            invoice.save()


    def __str__(self):
        return f"{self.allocation_number} - {self.allocated_amount}"

    class Meta:
        ordering = ['-allocation_date']
        verbose_name = "Purchase Payment Allocation"
        verbose_name_plural = "Purchase Payment Allocations"