from django.db import models
from company.models.company_model import Company
from users.models.user_model import User
from config.models.create_update_base_model import CreateUpdateBaseModel
import uuid



class StockTake(CreateUpdateBaseModel):
    # Model representing a stock take event in inventory
    PREFIX = 'ST'
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='stock_takes')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='stock_takes')
    quantity_counted = models.PositiveIntegerField(default=0)
    performed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='stock_takes')
    stock_take_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending', help_text="Status of the stock take")
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Optional reference number for tracking")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_finalized = models.BooleanField(default=False)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_stock_takes')
    rejected_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_stock_takes')
    rejection_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-stock_take_date']

    def __str__(self):
        return f"StockTake at {self.stock_take_date} for {self.company.name} - {self.branch.name} branch"
    

    @staticmethod
    def generate_reference_number():
        return f'{StockTake.PREFIX}-{str(uuid.uuid4()).split("-")[0].upper()}'