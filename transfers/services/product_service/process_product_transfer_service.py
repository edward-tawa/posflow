from transfers.services.transfer_service import TransferService
from transactions.models.transaction_model import Transaction
from transfers.models.transfer_model import Transfer
from transfers.models.product_transfer_model import ProductTransfer
from transfers.services.product_service.product_transfer_service import ProductTransferService
from transfers.services.product_service.product_transfer_item_service import ProductTransferItemService
from transfers.models.product_transfer_item_model import ProductTransferItem
from transactions.services.transaction_service import TransactionService
from accounts.services.branch_account_service import BranchAccountService
from inventory.services.product_stock.product_stock_service import ProductStockService
from company.models.company_model import Company
from branch.models.branch_model import Branch
from inventory.models.product_model import Product
from dataclasses import dataclass
from loguru import logger
from django.db import transaction as db_transaction


@dataclass
class ProcessTransferResult:
    product_transfer: ProductTransfer
    product_transfer_items: list[ProductTransferItem]
    transaction: Transaction


class ProcessTransferService:
    # -------------------------
    # PROCESS PRODUCT TRANSFER
    # -------------------------

    @staticmethod
    @db_transaction.atomic
    def process_product_transfer(
        *,
        transfer: Transfer,
        company: Company,
        source_branch: Branch,
        destination_branch: Branch,
        products_list: list[Product],
        quantity: int = 1,
    ) -> ProcessTransferResult:
        """Processes a product transfer by creating product transfer items."""
        try:


            # Create Product Transfer
            product_transfer = ProductTransferService.create_product_transfer(
                transfer=transfer,
                company=company,
                source_branch=source_branch,
                destination_branch=destination_branch,
            )

            # Create Product Transfer Items
            transfer_products = ProductTransferItemService.create_product_transfer_items(
                product_transfer_item_data=[
                    {
                        "transfer": transfer,
                        "product_transfer": product_transfer,
                        "company": company,
                        "branch": source_branch,
                        "product": product,
                        "quantity": quantity,
                        "unit_price": product.unit_price, 
                    }
                    for product in products_list
                ]
            )


            # Update Transfer Total Amount
            transfer.update_total_amount()


            # Move Stock
            ProductStockService.decrease_stock_for_transfer(transfer)
            ProductStockService.increase_stock_for_transfer(transfer)

            
            # Get brannch accounts
            source_branch_account = BranchAccountService.get_or_create_branch_account(
                company=company,
                branch=source_branch
            )

            
            destination_branch_account = BranchAccountService.get_or_create_branch_account(
                company=company,
                branch=destination_branch
            )


            # Record Transaction
            transaction = TransactionService.create_transaction(
                company=company,
                branch=source_branch,
                debit_account=source_branch_account.account,
                credit_account=destination_branch_account.account,
                transaction_type="PRODUCT_TRANSFER",
                transaction_category="TRANSFER",
                total_amount=transfer.total_amount,
            )

            # Apply Transaction to Accounts
            TransactionService.apply_transaction_to_accounts(
                transaction
            )


            # Mark completed
            transfer.status = 'completed'
            transfer.save(update_fields=['status'])

            logger.info(
                f"Processed Product Transfer '{product_transfer.pk}' "
                f"with {len(transfer_products)} items for Transfer '{transfer.reference_number}'."
            )

            
            # --------------- RETURN RESULT ---------------
            return ProcessTransferResult(
                product_transfer=product_transfer,
                product_transfer_items=transfer_products,
                transaction=transaction
            )

        
        
        except Exception as e:
            logger.error(f"Error processing product transfer: {e}")
            raise