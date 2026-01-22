from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from django.db.models import F, Sum
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
    currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='sales_invoices')
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
        """
        Generates a unique invoice number.
        """
        return f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"

    def update_total_amount(self):
        """
        Updates the total_amount based on associated invoice items.
        """
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or 0  # fallback to 0 if there are no items
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure an invoice number is generated if not already set.
        """
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the SalesInvoice instance.
        """
        return f"Invoice {self.invoice_number} - {self.customer}"

    class Meta:
        # Database indexes for optimized queries
        indexes = [
            models.Index(fields=["company", "branch", "invoice_date"]),
            models.Index(fields=["issued_by"]),
        ]