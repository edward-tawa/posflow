from sales.services.sales_order_item_service import SalesOrderItemService
from sales.models.sales_order_item_model import SalesOrderItem
from sales.models.sales_order_model import SalesOrder



def create_sales_order_items_util(
        sales_order: SalesOrder,
        items_data: list,
) -> list[SalesOrderItem]:
    """
    Utility function to create multiple sales order items.
    """

    if not items_data:
        raise ValueError("items_data cannot be empty.")

    required_fields = {"product", "product_name", "quantity", "unit_price"}

    sales_order_items = []

    for idx, item_data in enumerate(items_data):
        missing = required_fields - item_data.keys()
        if missing:
            raise ValueError(
                f"Item at index {idx} is missing fields: {missing}"
            )

        sales_order_item = SalesOrderItemService.create_sales_order_item(
            sales_order=sales_order,
            product=item_data["product"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            tax_rate=item_data.get("tax_rate", 0),
        )

        sales_order_items.append(sales_order_item)

    return sales_order_items