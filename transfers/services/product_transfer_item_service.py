from transfers.models.product_transfer_item_model import ProductTransferItem
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger
from company.models import Company
from branch.models import Branch
from inventory.models import Product
from users.models import User

class ProductTransferItemError(Exception):
    """Custom exception for ProductTransferItem domain errors."""
    pass


class ProductTransferItemService:

    ALLOWED_UPDATE_FIELDS = {"quantity"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_product_transfer_item(
        *,
        transfer: Transfer,
        product_transfer,
        company: Company,
        branch: Branch,
        product: Product,
        quantity: int
    ) -> ProductTransferItem:
        item = ProductTransferItem.objects.create(
            transfer=transfer,
            product_transfer=product_transfer,
            company=company,
            branch=branch,
            product=product,
            quantity=quantity
        )
        logger.info(
            f"Product Transfer Item '{item.product.name}' created for transfer '{transfer.id}'."
        )

        if item.transfer:
            item.transfer.update_total_amount()
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_product_transfer_item(
        item: ProductTransferItem,
        *,
        quantity: int | None = None
    ) -> ProductTransferItem:

        updated_fields = []

        if quantity is not None:
            item.quantity = quantity
            updated_fields.append("quantity")

        if updated_fields:
            item.save(update_fields=updated_fields)
            logger.info(
                f"Product Transfer Item '{item.product.name}' updated: {', '.join(updated_fields)}"
            )
            if item.transfer:
                item.transfer.update_total_amount()

        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_product_transfer_item(item: ProductTransferItem) -> None:
        transfer = item.transfer
        item_name = item.product.name
        item.delete()
        logger.info(f"Product Transfer Item '{item_name}' deleted.")
        if transfer:
            transfer.update_total_amount()

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_transfer(item: ProductTransferItem, transfer: Transfer) -> ProductTransferItem:
        previous_transfer = item.transfer
        item.transfer = transfer
        item.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer Item '{item.product.name}' attached to transfer "
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
            f"Product Transfer Item '{item.product.name}' detached from transfer "
            f"'{previous_transfer.id if previous_transfer else 'None'}'."
        )

        if previous_transfer:
            previous_transfer.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def attach_to_product_transfer(
        item: ProductTransferItem,
        product_transfer
    ) -> ProductTransferItem:
        previous_product_transfer = item.product_transfer
        item.product_transfer = product_transfer
        item.save(update_fields=['product_transfer'])
        logger.info(
            f"Product Transfer Item '{item.product.name}' attached to product transfer "
            f"'{product_transfer.id}' (previous product transfer: "
            f"'{previous_product_transfer.id if previous_product_transfer else 'None'}')."
        )

        return item
    
    @staticmethod
    @db_transaction.atomic
    def detach_from_product_transfer(item: ProductTransferItem) -> ProductTransferItem:
        previous_product_transfer = item.product_transfer
        item.product_transfer = None
        item.save(update_fields=['product_transfer'])
        logger.info(
            f"Product Transfer Item '{item.product.name}' detached from product transfer "
            f"'{previous_product_transfer.id if previous_product_transfer else 'None'}'."
        )

        return item