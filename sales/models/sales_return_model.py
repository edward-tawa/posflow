from django.db import models, transaction
from loguru import logger
from config.models.create_update_base_model import CreateUpdateBaseModel
import uuid




class SalesReturn(CreateUpdateBaseModel):
    PREFIX = 'SR'

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='sales_returns')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='sales_returns')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='sales_returns')
    sale_order = models.ForeignKey('sales.SalesOrder', on_delete=models.CASCADE, related_name='sales_returns')  
    return_number = models.CharField(max_length=20, unique=True)
    return_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='processed_sales_returns')
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)

    def generate_return_number(self):
        """Generates a unique return number for the sales return."""
        return_number = f"{self.PREFIX}-{str(uuid.uuid4()).split('-')[0].upper()}"
        logger.info(f"Generated return number successfully: {return_number}")
        return return_number
    
    @transaction.atomic
    def update_total_amount(self):
        """Updates the total amount based on related sales return items."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        logger.info(f"Updated total amount for return {self.return_number}: {self.total_amount}")
        self.save(update_fields=['total_amount'])
        

    def save(self, *args, **kwargs):
        # Auto-generate return number once on creation
        if not self.return_number:
            self.return_number = self.generate_return_number()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Return {self.return_number} - {self.customer_name}"
    

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "return_date"]),
            models.Index(fields=["sale_order"]),
            models.Index(fields=["processed_by"]),
        ]

    