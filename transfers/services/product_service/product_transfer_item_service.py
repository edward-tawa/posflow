from transfers.models.product_transfer_item_model import ProductTransferItem
from transfers.models.transfer_model import Transfer
from transfers.models.product_transfer_model import ProductTransfer
from transfers.exceptions.product_transfer_item.product_transfer_item_exception import (
    ProductTransferItemListEmpty,
    ProductTransferItemDuplicateError,
    ProductTransferItemNotFound,
    ProductTransferItemQuantityError,
    InsufficientQuantityError,
    ProductTransferItemStatusError,
    ProductTransferItemDatabaseError,
    
)
from django.db import IntegrityError, DatabaseError, transaction as db_transaction
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
        product_transfer: ProductTransfer,
        company: Company,
        product: Product,
        quantity: int,
        unit_price: float = None,
    ) -> ProductTransferItem:
        item = ProductTransferItem.objects.create(
            transfer=transfer,
            product_transfer=product_transfer,
            company=product.company,
            product=product,
            quantity=quantity,
            unit_price=product.unit_price
        )

        logger.info(
            f"Product Transfer Item '{item.product.name}' created for transfer '{transfer.id}'."
        )

        # add to product transfer
        ProductTransferItemService.add_to_product_transfer(item=item, product_transfer=product_transfer)
        
        return item
    

    @staticmethod
    @db_transaction.atomic
    def create_product_transfer_items(
        *,
        product_transfer_item_data: list[dict],
    ):
        
        """
        creates product transfer items in bulk.
        """

        for item in product_transfer_item_data:
            transfer: Transfer = item["transfer"]
            item["company"] = transfer.company
            item["branch"] = transfer.source_branch


        if len(product_transfer_item_data) < 1:
            raise ProductTransferItemListEmpty("The product transfer item data list is empty.")
        
        if len(product_transfer_item_data) != len(set(
            (item["product"].id, item["transfer"].id) for item in product_transfer_item_data)):
            raise ProductTransferItemDuplicateError("Duplicate product transfer items found in the input data.")

        created = ProductTransferItem.objects.bulk_create(
            [ProductTransferItem(**data) for data in product_transfer_item_data]    
        )
    
        logger.info(
            f"Bulk created {len(created)} Product Transfer Items."
        )

        return created
    
    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_product_transfer_item(*,
        item: ProductTransferItem,
        quantity: int | None = None
    ) -> ProductTransferItem:

        updated_fields = []

        if quantity is None:
            raise ProductTransferItemQuantityError("No quantity provided for update.")
        
        if quantity <= 0:
            raise InsufficientQuantityError("Quantity can not be or less than zero.")
        
        if quantity is not None:
            item.quantity = quantity
            updated_fields.append("quantity")

        if updated_fields:
            item.save(update_fields=updated_fields)
            logger.info(
                "Updated ProductTransferItem",
                extra={
                    "product": item.product.id,
                    "item_id": item.id,
                    "fields": updated_fields,
                },
            )
            
        if item.transfer:
            transfer: Transfer = item.transfer
            transfer.update_total_amount()

        return item
    

    @staticmethod
    def get_product_transfer_item(*,
        transfer: Transfer,
        product: Product,
    ):
        try:
            
            if transfer is None or product is None:
                raise ProductTransferItemNotFound("Transfer or Product is None.")
            
            if transfer.status in ["PENDING", "CANCELLED"]:
                raise ProductTransferItemStatusError(
                    "Cannot retrieve items from a pending or cancelled transfer."
                )
            
            item = ProductTransferItem.objects.get(
                transfer=transfer,
                product=product,
            )
            return item
        
        except ProductTransferItem.DoesNotExist:
        
            logger.error(
                f"Product Transfer Item for product '{product.name}' in transfer '{transfer.id}' does not exist."
            )
            raise ProductTransferItemNotFound(
                f"Product Transfer Item for product '{product.name}' in transfer '{transfer.id}' does not exist."
            )
    
        except (IntegrityError, DatabaseError) as e:
            logger.error(
                f"Database error while retrieving Product Transfer Item for product '{product.name}' in transfer '{transfer.id}': {str(e)}"
            )
            raise ProductTransferItemDatabaseError(
                "A database error occurred while retrieving the product transfer item."
            )
        
    @staticmethod
    def get_product_transfer_item_by_id(
        item_id: int,
    ) -> ProductTransferItem | None:
        try:
            if item_id is None:
                raise ProductTransferItemNotFound("Product Transfer Item ID is None.")
            item = ProductTransferItem.objects.get(id=item_id)
            return item
        except ProductTransferItem.DoesNotExist:
            raise ProductTransferItemNotFound(f"Product Transfer Item with ID '{item_id}' does not exist.")

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_product_transfer_item(item: ProductTransferItem) -> None:
        transfer: Transfer = item.transfer
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
    def add_to_product_transfer(*,
        item: ProductTransferItem,
        product_transfer: ProductTransfer
    ) -> ProductTransferItem:
        item.product_transfer = product_transfer
        item.save(update_fields=['product_transfer'])
        logger.info(
            f"Product Transfer Item '{item.product.name}' added to product transfer"
            f"'{product_transfer.id}'."
        )
        transfer: Transfer = product_transfer.transfer
        if transfer:
            transfer.update_total_amount()
        return item
    
    @staticmethod
    @db_transaction.atomic
    def remove_from_product_transfer(item: ProductTransferItem) -> ProductTransferItem:
        """
        Docstring for remove_from_product_transfer
        Removes the given ProductTransferItem from its associated ProductTransfer.
        Updates the total amount of the associated Transfer if applicable.
        """

        if item is None:
            raise ProductTransferItemNotFound("Product Transfer Item is None.")\
            
        if item.product_transfer is None:
            raise ProductTransferItemStatusError(
                "Product Transfer Item is not associated with any Product Transfer."
            )

        try:
            previous_product_transfer: ProductTransfer = item.product_transfer
            item.product_transfer = None
            item.save(update_fields=['product_transfer'])
            logger.info(
                f"Product Transfer Item '{item.product.name}' removed from product transfer"
                f"'{previous_product_transfer.id if previous_product_transfer else 'None'}'."
            )
            transfer: Transfer = previous_product_transfer.transfer
            if transfer:
                transfer.update_total_amount()
            return item
        
        except (IntegrityError, DatabaseError) as e:
            logger.error(
                f"Database error while removing Product Transfer Item '{item.product.name}' from product transfer: {str(e)}"
            )
            raise ProductTransferItemDatabaseError(
                "A database error occurred while removing the product transfer item from the product transfer."
            )