from transfers.services.product_transfer_service import ProductTransferService
from transfers.models.product_transfer_model import ProductTransfer



def add_product_transfer_to_transfer_util(
        *,
        product_transfer,
        company,
        branch,
        reference_number
) -> ProductTransfer:
    """
    Utility function to add a product transfer to a transfer.
    """
    transfer = ProductTransferService.get_product_transfer(
        company=company,
        source_branch=branch,
        reference_number=reference_number,
    )

    ProductTransferService.add_to_transfer(
        product_transfer=product_transfer,
        transfer=transfer
    )
    return product_transfer