from sales.services.sales_invoice_item_service import SalesInvoiceItemService
from sales.models.sales_invoice_item_model import SalesInvoiceItem
from sales.models.sales_invoice_model import SalesInvoice



def create_sales_invoice_items_util(
        sales_invoice: SalesInvoice,
        items_data: list,
) -> list[SalesInvoiceItem]:
    """
    Utility function to create multiple sales invoice items.
    """

    if not items_data:
        raise ValueError("items_data cannot be empty.")

    required_fields = {"product", "product_name", "quantity", "unit_price"}

    sales_invoice_items = []

    for idx, item_data in enumerate(items_data):
        missing = required_fields - item_data.keys()
        if missing:
            raise ValueError(
                f"Item at index {idx} is missing fields: {missing}"
            )

        sales_invoice_item = SalesInvoiceItemService.create_sales_invoice_item(
            sales_invoice=sales_invoice,
            product=item_data["product"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            tax_rate=item_data.get("tax_rate", 0),
        )

        sales_invoice_items.append(sales_invoice_item)

    return sales_invoice_items