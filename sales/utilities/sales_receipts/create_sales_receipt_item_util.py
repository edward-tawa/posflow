from sales.services.sales_receipt_item_service import SalesReceiptItemService
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt



def create_sales_receipt_item_util(
        sales_order: SalesOrder,
        sales_receipt: SalesReceipt,
):
    """
    Utility that creates sales receipt items for all items in the sales order
    by orchestrating the SalesReceiptItemService.
    """
    created_items = []

    for order_item in sales_order.items.all():
        item = SalesReceiptItemService.create_sales_receipt_item(
            sales_receipt=sales_receipt,
            product=order_item.product,
            product_name=order_item.product_name,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            tax_rate=order_item.tax_rate
        )
        created_items.append(item)

    return created_items
