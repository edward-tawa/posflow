from transfers.services.product_service.product_transfer_service import ProductTransferService
from transfers.models.product_transfer_model import ProductTransfer



def create_product_transfer_util(
        *,
        transfer,
        company,
        source_branch,
        destination_branch,
        notes="",
        created_by=None
) -> ProductTransfer:
    """
    Utility function to create a product transfer.
    """
    product_transfer = ProductTransferService.create_product_transfer(
        transfer=transfer,
        company=company,
        source_branch=source_branch,
        destination_branch=destination_branch,
        notes=notes,
        created_by=created_by
    )
    return product_transfer