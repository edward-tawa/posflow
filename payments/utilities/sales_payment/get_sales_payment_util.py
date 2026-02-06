from payments.services.sales.sales_payment_service import SalesPaymentService
from payments.models.payment_model import Payment
from payments.models.sales_payment_model import SalesPayment
from typing import Union
from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_order_model import SalesOrder



def get_sales_payment_util(*, company, branch, obj: Union[SalesOrder, SalesInvoice], payment: Payment) -> SalesPayment:
    """
    Utility function to get a sales payment by ID.
    """
    sales_payment = SalesPaymentService.get_sales_payment(
        company=company,
        branch=branch,
        obj=obj,
        payment=payment
    )
    return sales_payment