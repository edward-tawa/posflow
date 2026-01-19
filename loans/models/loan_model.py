from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel




class Loan(CreateUpdateBaseModel):
    borrower = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='loans'
    )
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    start_date = models.DateField()
    end_date = models.DateField()
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_loans'
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Loan {self.id} for {self.borrower.first_name} - Amount: {self.loan_amount}"

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Loan"
        verbose_name_plural = "Loans"
        
        indexes = [
            models.Index(fields=['borrower']),
            models.Index(fields=['issued_by']),
        ]

    