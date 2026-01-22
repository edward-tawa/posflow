from sales.services.sales_order_service import SalesOrderService
from sales.models.sales_order_model import SalesOrder



def create_sales_order_util(
        company,
        branch,
        customer,
        sales_person,
        notes: str = None,
) -> SalesOrder:
    """
    Utility function to create a sales order.
    """
    sales_order = SalesOrderService.create_sales_order(
        company=company,
        branch=branch,
        customer=customer,
        sales_person=sales_person,
        notes=notes,
    )
    return sales_order