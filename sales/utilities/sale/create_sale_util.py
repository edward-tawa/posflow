from sales.services.sale_service import SaleService
from sales.models.sale_model import Sale


def create_sale_util(
        company,
        branch,
        customer,
        sale_type,
        sales_invoice,
        sale_receipt,
        issued_by = None,
        notes: str = None,
) -> Sale:
    """
    Utility function to create a sale.
    """
    sale = SaleService.create_sale(
        company=company,
        branch=branch,
        customer=customer,
        sale_type=sale_type,
        sales_invoice=sales_invoice,
        sale_receipt=sale_receipt,
        issued_by=issued_by,
        notes=notes,
    )
    return sale