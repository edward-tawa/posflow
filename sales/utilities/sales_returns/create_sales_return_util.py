from sales.services.sales_return_service import SalesReturnService
from sales.models.sales_return_model import SalesReturn


def create_sales_return_util(
        company,
        branch,
        customer,
        sales_order,
        sale,
        return_date,
        processed_by,
        notes,
):
    """
    Utility function to create a sales return.
    """
    sales_return = SalesReturnService.create_sales_return(
        company=company,
        branch=branch,
        customer=customer,
        sales_order=sales_order,
        sale=sale,
        return_date=return_date,
        processed_by=processed_by,
        notes=notes,
    )
    return sales_return