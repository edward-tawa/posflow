from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid



class SalesInvoice(CreateUpdateBaseModel):
    PREFIX = 'INVOICE'
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ISSUED', 'Issued'),
        ('VOIDED', 'Voided'),
        ('PAID', 'Paid'),  # if you track payment
    ]

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='sales_invoices')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='sales_invoices')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='sales_invoices')
    sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_invoices')
    sales_order = models.ForeignKey('sales.SalesOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_invoices')
    receipt = models.ForeignKey('sales.SalesReceipt', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_invoices')
    
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_voided = models.BooleanField(default=False)
    void_reason = models.TextField(blank=True, null=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    issued_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='issued_sales_invoices')
    notes = models.TextField(blank=True, null=True)


    def generate_invoice_number(self):
        return f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"

    def update_total_amount(self):
        total = sum(item.unit_price * item.quantity for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer}"

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "invoice_date"]),
            models.Index(fields=["issued_by"]),
        ]