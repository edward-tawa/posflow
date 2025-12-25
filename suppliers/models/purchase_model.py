from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class Purchase(CreateUpdateBaseModel):
    PREFIX = 'PURCHASE'

    PURCHASE_TYPE = [
        ('CASH', 'Cash'),
        ('CREDIT', 'Credit')
    ]

    PAYMENT_STATUS = [
        ('FULLY_PAID', 'Fully Paid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('UNPAID', 'Unpaid')
    ]

    company = models.ForeignKey(
        'company.Company', on_delete=models.CASCADE, related_name='purchases'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.CASCADE, related_name='purchases'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier', on_delete=models.CASCADE, related_name='purchases'
    )
    purchase_order = models.ForeignKey(
        'suppliers.PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases'
    )
    purchase_invoice = models.ForeignKey(
        'suppliers.PurchaseInvoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases'
    )
    supplier_receipt = models.ForeignKey(
        'suppliers.SupplierReceipt', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases'
    )
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS, default='UNPAID'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_TYPE, default='CASH')
    purchase_number = models.CharField(max_length=20, unique=True)
    issued_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='issued_purchases'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "purchase_date"]),
            models.Index(fields=["supplier"]),
        ]

    def __str__(self):
        return f"Purchase {self.purchase_number} - {self.supplier}"

    def generate_purchase_number(self):
        """Generate a unique purchase number."""
        self.purchase_number = f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Generated purchase number: {self.purchase_number}")

    def save(self, *args, **kwargs):
        """Override save to ensure purchase_number is set."""
        if not self.purchase_number:
            self.generate_purchase_number()
        super().save(*args, **kwargs)
        logger.info(f"Saved purchase with purchase number: {self.purchase_number}")
