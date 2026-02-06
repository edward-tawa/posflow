from payments.services.sales.sales_payment_service import SalesPaymentService
from payments.models.payment_model import Payment
from payments.models.sales_payment_model import SalesPayment




def add_sales_payment_to_payment_util(*,sales_payment, payment) -> SalesPayment:
    """
    Utility function to add a sales payment to an existing payment.
    """
    SalesPaymentService.add_sales_payment_to_payment(
        sales_payment=sales_payment,
        payment=payment
    )
    