from sales.services.sales_quotation_item_service import SalesQuotationItemService
from sales.models.sales_quotation_item_model import SalesQuotationItem
from sales.models.sales_quotation_model import SalesQuotation


def create_sales_quotation_items_util(
        sales_quotation: SalesQuotation,
        items_data: list,
) -> list[SalesQuotationItem]:
    """
    Utility function to create multiple sales quotation items.
    """

    if not items_data:
        raise ValueError("items_data cannot be empty.")

    required_fields = {"product", "product_name", "quantity", "unit_price"}

    sales_quotation_items = []

    for idx, item_data in enumerate(items_data):
        missing = required_fields - item_data.keys()
        if missing:
            raise ValueError(
                f"Item at index {idx} is missing fields: {missing}"
            )

        sales_quotation_item = SalesQuotationItemService.create_sales_quotation_item(
            sales_quotation=sales_quotation,
            product=item_data["product"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            tax_rate=item_data.get("tax_rate", 0),
        )

        sales_quotation_items.append(sales_quotation_item)

    return sales_quotation_items