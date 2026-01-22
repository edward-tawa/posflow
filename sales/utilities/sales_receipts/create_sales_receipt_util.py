from sales.services.sales_receipt_service import SalesReceiptService
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt



def create_sales_receipt_util(
        sale,
        sales_order,
        customer,
        branch,
        company,
        issued_by,
        total_amount,
        notes=None
    ):
    """
    Utility that creates a receipt by ochestrating the SalesReceiptService 
    """
    # Create the sales receipt using the service
    receipt, updated_sales_order = SalesReceiptService.create_sales_receipt(
        sale=sale,
        sales_order=sales_order,
        customer=customer,
        branch=branch,
        company=company,
        issued_by=issued_by,
        total_amount=total_amount,
        notes=notes
    )

    return receipt, updated_sales_order