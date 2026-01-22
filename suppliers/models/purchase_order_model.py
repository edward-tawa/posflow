from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel
from suppliers.models.supplier_model import Supplier
import uuid



class PurchaseOrder(CreateUpdateBaseModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.CASCADE, related_name='purchase_orders')
    quantity_ordered = models.PositiveIntegerField()
    order_date = models.DateField(auto_now_add=True)
    delivery_date = models.DateField(blank=True, null=True)
    currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='purchase_orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ], default='pending', help_text="Status of the purchase order")
    reference_number = models.CharField(max_length=10, blank=True, null=True, help_text="Optional reference number for tracking")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('company', 'reference_number')
        ordering = ['-order_date']

    
    def generate_reference_number(self):
        """Generate a 6-character uppercase reference code."""
        return uuid.uuid4().hex[:6].upper()
    
    def update_total_amount(self):
        """Recalculate and update the total amount based on associated items."""
        total = sum(item.total_amount for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PurchaseOrder {self.reference_number} for {self.company.name} from {self.supplier.name}"