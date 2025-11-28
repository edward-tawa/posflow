from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from decimal import Decimal, ROUND_HALF_UP
from loguru import logger


class PaymentMethod(CreateUpdateBaseModel):
    PREFIX = 'PM'

    PAYMENT_METHOD = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('mobile_payment', 'Mobile Payment'),
        ('ecocash', 'Ecocash'),
        ('other', 'Other'),
    ]
    
    PAYMENT_CODE = [
        ('CR', 'Credit Card'),
        ('DC', 'Debit Card'),
        ('BT', 'Bank Transfer'),
        ('CA', 'Cash'),
        ('MP', 'Mobile Payment'),
        ('ECO', 'Ecocash'),
        ('OT', 'Other'),
    ]

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    is_active = models.BooleanField(default=True)
    payment_method_name = models.CharField(max_length=50, choices=PAYMENT_METHOD, default='cash')
    payment_method_code = models.CharField(max_length=20, choices=PAYMENT_CODE, unique=True, editable=False, default='CA')

    def save(self, *args, **kwargs):
        # Auto-generate payment method code if not provided
        if not self.payment_method_code:
            self.payment_method_code = self.generate_payment_method_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_method_name} - {'Active' if self.is_active else 'Inactive'}"

    class Meta:
        ordering = ['payment_method_name']
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
