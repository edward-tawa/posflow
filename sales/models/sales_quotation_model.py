from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid



class SalesQuotation(CreateUpdateBaseModel):
    Prefix = "SQ"
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='sales_quotations')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='sales_quotations') 
    quotation_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='sales_quotations')
    quotation_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_sales_quotations')
    notes = models.TextField(blank=True, null=True)


    def generate_quotation_number(self):
        quotation_number =  f"{self.Prefix}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Generated quotation number successfully: {quotation_number}")
        return quotation_number
    
    def update_total_amount(self):
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        logger.info(f"Updated total amount for quotation {self.quotation_number}: {self.total_amount}")
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        # Auto-generate quotation number once on creation
        if not self.quotation_number:
            self.quotation_number = self.generate_quotation_number()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quotation {self.quotation_number} - {self.customer.name}"
    
    class Meta:
        indexes = [
            models.Index(fields=["company", "quotation_date"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["created_by"]),
        ]