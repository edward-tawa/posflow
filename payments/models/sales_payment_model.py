from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel



class SalesPayment(CreateUpdateBaseModel):
    
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='sales_payments'
    )
    
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='sales_payments'
    )

    # might need to be removed
    sales_order = models.ForeignKey(
        'sales.SalesOrder',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )

    # might need to be removed
    sales_invoice = models.ForeignKey(
        'sales.SalesInvoice',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )

    sales_receipt = models.ForeignKey(
        'sales.SalesReceipt',
        on_delete=models.CASCADE,
        related_name='sales_payments',
        null=True,
        blank=True
    )

    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='sales_payments'
    )

    payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        on_delete=models.CASCADE,
        related_name='sales_payments'
    )

    received_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_sales_payments'
    )


    def __str__(self):
        return f"Payment {self.id} for Sales Order {self.sales_order.id}"