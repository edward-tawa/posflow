from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class ExpensePayment(CreateUpdateBaseModel):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='expense_payments'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='expense_payments'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='expense_payments'
    )
    payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        on_delete=models.CASCADE,
        related_name='expense_payments'
    )
    expense = models.ForeignKey(
        'expenses.Expense',
        on_delete=models.CASCADE,
        related_name='expense_payments'
    )
    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_expense_payments'
    )

    class Meta:
        models.Index(fields=['payment', 'expense'])
        models.Index(fields=['company', 'branch'])
        models.Index(fields=['issued_by'])

        models.UniqueConstraint(fields=['payment', 'expense'], name='unique_payment_expense')

    def __str__(self):
        return f"Payment {self.id} for Expense {self.expense.id}"

    