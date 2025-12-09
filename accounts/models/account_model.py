from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid



class Account(CreateUpdateBaseModel):
    ACCOUNT_TYPES = [
    ('BRANCH', 'Branch Account'),
    ('CUSTOMER', 'Customer Account'),
    ('SUPPLIER', 'Supplier Account'),
    ('EMPLOYEE', 'Employee Account'),
    ('LOAN', 'Loan Account'),
    ('CASH', 'Cash Account'),
    ('BANK', 'Bank Account'),
    ('ECOCASH', 'Ecocash Account'),
    ('MOBILE_MONEY', 'Mobile Money Account'),
    ('PAYPAL', 'Paypal Account'),
    ('EQUITY', 'Equity Account'),
    ('INCOME', 'Income Account'),
    ('EXPENSE', 'Expense Account'),
    ]

    name = models.CharField(max_length=255)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='accounts')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='accounts', null=True, blank=True)
    account_number = models.CharField(max_length=100, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)


    def generate_account_number(self):
        while True:
            account_number = str(uuid.uuid4()).replace('-', '')[:12].upper()
            if not Account.objects.filter(account_number=account_number).exists():
                logger.info(f"Generated account number: {account_number} successfully.")
                return account_number
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Account {self.name} ({self.account_number})"
    

    class Meta:
        unique_together = ('company', 'name')