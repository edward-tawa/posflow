from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class SalesOrder(CreateUpdateBaseModel):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        CONFIRMED = 'confirmed', 'Confirmed'
        PAID = 'paid', 'Paid'
        DISPATCHED = 'dispatched', 'Dispatched'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    
    PREFIX = 'SO'

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='sales_orders')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='sales_orders')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='sales_orders')
    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100)
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cashier = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='processed_sales_orders')
    notes = models.TextField(blank=True, null=True)

    def generate_unique_order_number(self):
        while True:
            number = f"{self.PREFIX}-{uuid.uuid4().hex[:6].upper()}"
            if not SalesOrder.objects.filter(order_number=number).exists():
                return number

    def update_total_amount(self):
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_unique_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"

    class Meta:
        indexes = [
            models.Index(fields=["company", "branch", "order_date"]),
            models.Index(fields=["status"]),
        ]
