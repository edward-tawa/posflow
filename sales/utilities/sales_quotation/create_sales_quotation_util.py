from sales.services.sales_quotation_service import SalesQuotationService
from sales.models.sales_quotation_model import SalesQuotation


def create_sales_quotation_util(
        company,
        branch,
        customer,
        valid_until,
        created_by,
        notes,
        status="draft",
)->SalesQuotation:
    """
    Utility function to create a sales quotation.
    """
    sales_quotation = SalesQuotationService.create_sales_quotation(
        company=company,
        branch=branch,
        customer=customer,
        valid_until=valid_until,
        created_by=created_by,
        notes=notes,
        status=status,
    )
    return sales_quotation