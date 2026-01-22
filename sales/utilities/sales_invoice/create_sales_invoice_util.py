from sales.services.sales_invoice_service import SalesInvoiceService
from sales.models.sales_invoice_model import SalesInvoice



def create_sales_invoice_util(
        company,
        branch,
        customer,
        sale,
        sales_order,
        discount_amount=0.0,
        notes: str = None,
        issued_by = None,
) -> SalesInvoice:
    """
    Utility function to create a sales invoice.
    """
    sales_invoice = SalesInvoiceService.create_sales_invoice(
        company=company,
        branch=branch,
        customer=customer,
        sale=sale,
        sales_order=sales_order,
        discount_amount=discount_amount,
        notes=notes,
        issued_by=issued_by,
        
    )
    return sales_invoice