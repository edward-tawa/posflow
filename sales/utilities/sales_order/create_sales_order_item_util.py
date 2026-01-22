from sales.services.sales_order_item_service import SalesOrderItemService
from sales.models.sales_order_item_model import SalesOrderItem
from sales.models.sales_order_model import SalesOrder



def create_sales_order_item_util(
        sales_order: SalesOrder,
        product,
        product_name: str,
        quantity: int,
        unit_price,
        tax_rate,
    ) -> SalesOrderItem:
    """
    Utility function to create a sales order item.
    """
    sales_order_item = SalesOrderItemService.create_sales_order_item(
        sales_order=sales_order,
        product=product,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
        tax_rate=tax_rate,
    )
    return sales_order_item