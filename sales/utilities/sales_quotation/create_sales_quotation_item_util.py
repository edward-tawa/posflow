from sales.services.sales_quotation_item_service import SalesQuotationItemService
from sales.models.sales_quotation_item_model import SalesQuotationItem
from sales.models.sales_quotation_model import SalesQuotation


def create_sales_quotation_item_util(
        sales_quotation: SalesQuotation,
        product,
        product_name: str,
        quantity: int,
        unit_price,
        tax_rate,
) -> SalesQuotationItem:
    """
    Utility function to create a sales quotation item.
    """
    sales_quotation_item = SalesQuotationItemService.create_sales_quotation_item(
        sales_quotation=sales_quotation,
        product=product,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
        tax_rate=tax_rate,
    )
    return sales_quotation_item