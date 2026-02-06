from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class RefundPayment(CreateUpdateBaseModel):
    # Refund payment model

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='refund_payments'
    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='refund_payments'
    )

    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='refund_payments'
    )

    payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        on_delete=models.CASCADE,
        related_name='refund_payments'
    )

    refund = models.ForeignKey(
        'payments.Refund',
        on_delete=models.CASCADE,
        related_name='refund_payments'
    )
    
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_refund_payments'
    )

    class Meta:
        models.Index(fields=['payment', 'refund'])
        models.Index(fields=['company', 'branch'])
        models.Index(fields=['processed_by'])

        models.UniqueConstraint(fields=['payment', 'refund'], name='unique_payment_refund')

    def __str__(self):
        return f"Payment {self.id} for Refund {self.refund.id}"