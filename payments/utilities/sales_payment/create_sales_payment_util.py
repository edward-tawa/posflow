from payments.services.sales.sales_payment_service import SalesPaymentService
from payments.models.payment_model import Payment
from payments.models.sales_payment_model import SalesPayment


def create_sales_payment_util(*,
                              company,
                              branch,
                              sales_order,
                              sales_invoice,
                              payment,
                              payment_method,
                              received_by
                              ) -> SalesPayment:
    """
    Utility function to create a sales payment.
    """
    sales_payment = SalesPaymentService.create_sales_payment(
        company=company,
        branch=branch,
        sales_order=sales_order,
        sales_invoice=sales_invoice,
        payment=payment,
        payment_method=payment_method,
        received_by=received_by
    )
    return sales_payment