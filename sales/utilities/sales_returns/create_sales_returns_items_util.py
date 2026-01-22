from typing import List, Dict, Any
from django.db import transaction
from sales.services.sales_return_item_service import SalesReturnItemService
from sales.models.sales_return_item_model import SalesReturnItem
from sales.models.sales_return_model import SalesReturn


@transaction.atomic
def create_sales_return_items_util(
    sales_return: SalesReturn,
    items_data: List[Dict[str, Any]],
) -> List[SalesReturnItem]:
    """
    Utility function to create multiple sales return items.
    """

    if not items_data:
        raise ValueError("items_data cannot be empty.")

    required_fields = {"product", "product_name", "quantity", "unit_price"}

    sales_return_items = []

    for idx, item_data in enumerate(items_data):
        missing = required_fields - item_data.keys()
        if missing:
            raise ValueError(
                f"Item at index {idx} is missing fields: {missing}"
            )

        sales_return_item = SalesReturnItemService.create_sales_return_item(
            sales_return=sales_return,
            product=item_data["product"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            tax_rate=item_data.get("tax_rate", 0),
        )

        sales_return_items.append(sales_return_item)

    return sales_return_items
