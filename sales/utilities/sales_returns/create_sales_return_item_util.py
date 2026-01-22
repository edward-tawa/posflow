from sales.services.sales_return_item_service import SalesReturnItemService
from sales.models.sales_return_item_model import SalesReturnItem
from sales.models.sales_return_model import SalesReturn


def create_sales_return_item_util(
        sales_return: SalesReturn,
        product,
        product_name: str,
        quantity: int,
        unit_price,
        tax_rate,
) -> SalesReturnItem:
    """
    Utility function to create a sales return item.
    """
    sales_return_item = SalesReturnItemService.create_sales_return_item(
        sales_return=sales_return,
        product=product,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
        tax_rate=tax_rate,
    )
    return sales_return_item