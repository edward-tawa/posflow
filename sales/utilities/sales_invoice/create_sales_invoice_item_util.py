from sales.services.sales_invoice_item_service import SalesInvoiceItemService
from sales.models.sales_invoice_model import SalesInvoice



def create_sales_invoice_item_util(
        sales_invoice: SalesInvoice,
        product,
        product_name: str,
        quantity: int,
        unit_price,
        tax_rate,
):
    """
    Utility function to create a sales invoice item.
    """


    item = SalesInvoiceItemService.create_sales_invoice_item(
        sales_invoice=sales_invoice,
        product=product,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
        tax_rate=tax_rate,
    )
    return item