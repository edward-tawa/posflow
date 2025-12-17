from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger
import uuid



class Expense(CreateUpdateBaseModel):
    PREFIX = 'EX'
    EXPENSE_CATEGORY = [
        ('TRAVEL', 'Travel'),
        ('MEALS', 'Meals'),
        ('SUPPLIES', 'Supplies'),
        ('UTILITIES', 'Utilities'),
        ('RENT', 'Rent'),
        ('SALARIES', 'Salaries'),
        ('PETTYCASH', 'Pettycash'),
        ('MISC', 'Miscellaneous'),
    ]
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    expense_number = models.CharField(max_length=20, unique=True, editable=False)
    expense_date = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses'
    )
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('UPAID', 'Unpaid')], default='PENDING')
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORY)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    incurred_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incurred_expenses'
    )

    def generate_expense_number(self):
        """ Generate a unique expense number. """
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Generated Expense number: {number}")
        return number

    def save(self, *args, **kwargs):
        # Auto-generate expense number if not provided
        if not self.expense_number:
            self.expense_number = self.generate_expense_number()
        super().save(*args, **kwargs)