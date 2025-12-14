from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class Sale(CreateUpdateBaseModel):
    PREFIX = 'SALE'

    SALE_TYPE = [
        ('CASH', 'Cash'),
        ('CREDIT', 'Credit')
    ]

    PAYMENT_STATUS = [
        ('FULLY_PAID', 'Fully Paid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('UNPAID', 'Unpaid')
    ]

    company = models.ForeignKey(
        'company.Company', on_delete=models.CASCADE, related_name='sales'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.CASCADE, related_name='sales'
    )
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE, related_name='sales'
    )
    sales_invoice = models.ForeignKey(
        'sales.SalesInvoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales'
    )
    sales_receipt = models.ForeignKey(
        'sales.SalesReceipt', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales'
    )
    sales_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS, default='UNPAID'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_type = models.CharField(max_length=10, choices=SALE_TYPE, default='CASH')
    sale_number = models.CharField(max_length=20, unique=True)
    issued_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='issued_sales'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "sales_date"]),
            models.Index(fields=["customer"]),
        ]

    def __str__(self):
        return f"Sale {self.sale_number} - {self.customer}"

    def generate_sale_number(self):
        """Generate a unique sale number."""
        self.sale_number = f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Generated sale number: {self.sale_number}")

    def save(self, *args, **kwargs):
        """Override save to ensure sale_number is set."""
        if not self.sale_number:
            self.generate_sale_number()
        super().save(*args, **kwargs)
        logger.info(f"Saved sale with sale number: {self.sale_number}")
