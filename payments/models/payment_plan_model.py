from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
import uuid


class PaymentPlan(CreateUpdateBaseModel):
    PREFIX = 'PP'
    TERM_CHOICES = [
        ('paylater', 'Pay Later'),
        ('layby', 'Lay-by'),
        ('installment', 'Installment'),
    ]


    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='payment_plans'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='payment_plans'
    )
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, related_name='payment_plans')
    name = models.CharField(max_length=50, choices=TERM_CHOICES)
    requires_deposit = models.BooleanField(default=False)
    deposit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    max_duration_days = models.PositiveIntegerField(null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    is_active = models.BooleanField(default=True)


    def generate_reference_number(self):
        number = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
        return number
    
    def save(self, *args, **kwargs):
        # Auto-generate reference number if not provided
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
