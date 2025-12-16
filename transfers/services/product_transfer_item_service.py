from transfers.models.product_transfer_item_model import ProductTransferItem
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger

class ProductTransferItemError(Exception):
    """Custom exception for ProductTransferItem domain errors."""
    pass

class ProductTransferItemService:

    ALLOWED_UPDATE_FIELDS = {"product_name", "quantity", "unit_price", "total_price", "notes"}

    @staticmethod
    @db_transaction.atomic
    def create_product_transfer_item(**kwargs) -> ProductTransferItem:
        item = ProductTransferItem.objects.create(**kwargs)
        logger.info(
            f"Product Transfer Item '{item.product_name}' created for transfer "
            f"'{item.transfer.id if item.transfer else 'None'}'."
        )
        if item.transfer:
            item.transfer.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def update_product_transfer_item(item: ProductTransferItem, **kwargs) -> ProductTransferItem:
        updated_fields = []
        for key, value in kwargs.items():
            if key in ProductTransferItemService.ALLOWED_UPDATE_FIELDS:
                setattr(item, key, value)
                updated_fields.append(key)
            else:
                raise ProductTransferItemError(f"Field '{key}' cannot be updated.")

        if not updated_fields:
            return item

        item.save(update_fields=updated_fields)
        logger.info(f"Product Transfer Item '{item.product_name}' updated: {', '.join(updated_fields)}")

        if item.transfer:
            item.transfer.update_total_amount()

        return item

    @staticmethod
    @db_transaction.atomic
    def delete_product_transfer_item(item: ProductTransferItem) -> None:
        transfer = item.transfer
        item_name = item.product_name
        item.delete()
        logger.info(f"Product Transfer Item '{item_name}' deleted.")
        if transfer:
            transfer.update_total_amount()

    @staticmethod
    @db_transaction.atomic
    def attach_to_transfer(item: ProductTransferItem, transfer: Transfer) -> ProductTransferItem:
        previous_transfer = item.transfer
        item.transfer = transfer
        item.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer Item '{item.product_name}' attached to transfer "
            f"'{transfer.id}' (previous transfer: '{previous_transfer.id if previous_transfer else 'None'}')."
        )

        if previous_transfer:
            previous_transfer.update_total_amount()
        transfer.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def detach_from_transfer(item: ProductTransferItem) -> ProductTransferItem:
        previous_transfer = item.transfer
        item.transfer = None
        item.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer Item '{item.product_name}' detached from transfer "
            f"'{previous_transfer.id if previous_transfer else 'None'}'."
        )

        if previous_transfer:
            previous_transfer.update_total_amount()
        return item
