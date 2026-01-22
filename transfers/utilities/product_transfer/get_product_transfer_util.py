from transfers.services.product_transfer_service import ProductTransferService
from transfers.models.product_transfer_model import ProductTransfer



def get_product_transfer_util(
        *,
        company,
        source_branch,
        destination_branch,
) -> ProductTransfer:
    """
    Utility function to get a product transfer.
    """
    product_transfer = ProductTransferService.get_product_transfer(
        company=company,
        source_branch=source_branch,
        destination_branch=destination_branch,
    )
    return product_transfer