from transfers.services.product_service.product_transfer_service import ProductTransferService
from transfers.models.product_transfer_model import ProductTransfer


def remove_product_transfer_from_transfer_util(
        *,
        product_transfer,
        company,
        source_branch,
        reference_number
) -> ProductTransfer:
    """
    Utility function to remove a product transfer from a transfer.
    """
    transfer = ProductTransferService.get_product_transfer(
        company=company,
        source_branch=source_branch,
        reference_number=reference_number,
    )

    ProductTransferService.remove_from_transfer(
        product_transfer=product_transfer,
        transfer=transfer
    )
    return product_transfer