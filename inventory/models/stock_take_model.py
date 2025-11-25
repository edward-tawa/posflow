from django.db import models
from company.models.company_model import Company
from users.models.user_model import User
from config.models.create_update_base_model import CreateUpdateBaseModel
import uuid



class StockTake(CreateUpdateBaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_takes')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='stock_takes')
    quantity_counted = models.PositiveIntegerField()
    perfomed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_takes')
    counted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending', help_text="Status of the stock take")
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Optional reference number for tracking")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-counted_at']

    def __str__(self):
        return f"StockTake at {self.counted_at} for {self.company.name} - {self.branch.name} branch"
    

    @staticmethod
    def generate_reference_number():
        return str(uuid.uuid4()).split('-')[0].upper()