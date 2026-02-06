from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class SalesReceipt(CreateUpdateBaseModel):
    PREFIX = 'RECEIPT'
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('ISSUED', 'Issued'), ('VOIDED', 'Voided')]
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='sales_receipts')
    sales_payment = models.ForeignKey('payments.SalesPayment', on_delete=models.SET_NULL, null=True, related_name='sales_receipts')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='sales_receipts')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='sales_receipts')
    sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_receipts')
    sales_order = models.ForeignKey('sales.SalesOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_receipts')
    receipt_number = models.CharField(max_length=20, unique=True)
    receipt_date = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='sales_receipts')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_voided = models.BooleanField(default=False)
    void_reason = models.TextField(blank=True, null=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    issued_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='issued_sales_receipts')
    notes = models.TextField(blank=True, null=True)

    def generate_receipt_number(self):
        return f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"

    def update_total_amount(self):
        total = sum(item.unit_price * item.quantity for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.customer}"

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "receipt_date"]),
            models.Index(fields=["issued_by"]),
        ]
