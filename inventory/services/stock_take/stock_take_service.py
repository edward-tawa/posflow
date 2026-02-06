from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.services.product_stock.product_stock_service import ProductStockService
# from inventory.services.stock_take_item_service import StockTakeItemService
from inventory.services.stock_movement.stock_movement_service import StockMovementService
from inventory.services.stock_take.stock_take_reconciliation_service import StockTakeReconcialiationService
from django.db.models import Sum, F
from django.utils import timezone


class StockTakeService:
    @staticmethod
    @db_transaction.atomic
    def create_stock_take(company, branch, quantity_counted, performed_by, notes=""):
        """
        Creates a new stock take record.

        Args:
            company: The company conducting the stock take.
            branch: The branch where the stock take is performed.
            quantity_counted (int): The quantity counted during the stock take.
            performed_by: The user who performed the stock take.
            notes (str): Optional notes regarding the stock take.

        Returns:
            StockTake: The created stock take record.
        """
        try:
            stock_take: StockTake = StockTake.objects.create(
                    company=company,
                    branch=branch,
                    quantity_counted=0,
                    performed_by=performed_by,
                    notes=notes,
                    status="open",
                    started_at=timezone.now(),
            )
            logger.info(
                f"Stock take created: Company='{company.name}', Branch='{branch.name}', "
                f"Reference Number='{stock_take.reference_number}', Quantity Counted={quantity_counted}, Performed By='{performed_by.username}'"
            )
            return stock_take

        except Exception as e:
            logger.error(
                f"Failed to create stock take: Company='{company.name}', Branch='{branch.name}', Error={str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_stock_take(company, branch, stock_id=None, reference_number=None):
        """
        Retrieves an existing stock take by ID or creates a new one if not found.

        Args:
            company: The company conducting the stock take.
            branch: The branch where the stock take is performed.
            stock_id (int, optional): The ID of the stock take to retrieve.
            reference_number (str, optional): The reference number of the stock take to retrieve.
        
        """        
        if stock_id:
            try:
                stock_take = StockTake.objects.get(company=company, branch=branch, reference_number=reference_number)
                logger.info(
                    f"Stock take retrieved: Company='{company.name}', Branch='{branch.name}', "
                    f"Reference Number='{stock_take.reference_number}'"
                )
                return stock_take
            except StockTake.DoesNotExist:
                logger.warning(
                    f"Stock take ID '{stock_id}' not found for Company='{company.name}'. Creating new stock take."
                )
        return StockTakeService.create_stock_take(
            company=company,
            branch=branch,
        )

    
    @staticmethod
    @db_transaction.atomic
    def delete_stock_take(stock_take: StockTake):
        """
        Deletes a stock take record.

        Args:
            stock_take (StockTake): The stock take record to delete.

        Returns:
            None
        """
        try:
            reference_number = stock_take.reference_number
            stock_take.delete()
            logger.info(f"Stock take deleted: Reference Number='{reference_number}'")

        except Exception as e:
            logger.error(
                f"Failed to delete stock take: Reference Number='{stock_take.reference_number}', Error={str(e)}"
            )
            raise
    


    @staticmethod
    @db_transaction.atomic
    def approve_stock_take(stock_take: StockTake, approved_by):
        """
        Approves a stock take before adjustments are applied.
        """
        try:
            stock_take.status = "approved"
            stock_take.approved_by = approved_by
            stock_take.save()

            logger.info(
                f"Stock take approved: Ref='{stock_take.reference_number}', Approved By='{approved_by.username}'"
            )
            return stock_take
        except Exception as e:
            logger.error(
                f"Failed to approve stock take: Ref='{stock_take.reference_number}', Error={str(e)}"
            )
            raise


    
    @staticmethod
    @db_transaction.atomic
    def update_stock_take_status(stock_take: StockTake, new_status: str):
        """
        Updates the status of an existing stock take record.

        Args:
            stock_take (StockTake): The stock take record to update.
            new_status (str): The new status to set ('pending', 'completed', 'cancelled').

        Returns:
            StockTake: The updated stock take record.
        """
        try:
            if new_status not in dict(StockTake._meta.get_field('status').choices):
                raise ValueError(f"Invalid status '{new_status}' provided.")

            stock_take.status = new_status
            stock_take.save()
            logger.info(
                f"Stock take status updated: Reference Number='{stock_take.reference_number}', New Status='{new_status}'"
            )
            return stock_take

        except Exception as e:
            logger.error(
                f"Failed to update stock take status: Reference Number='{stock_take.reference_number}', Error={str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def reject_stock_take(stock_take: StockTake, rejected_by, reason=""):
        """
        Rejects a stock take and attaches a reason.
        """
        try:
            stock_take.status = "rejected"
            stock_take.rejected_by = rejected_by
            stock_take.rejection_reason = reason
            stock_take.save()

            logger.info(
                f"Stock take rejected: Ref='{stock_take.reference_number}', Rejected By='{rejected_by.username}', Reason='{reason}'"
            )
            return stock_take
        except Exception as e:
            logger.error(
                f"Failed to reject stock take: Ref='{stock_take.reference_number}', Error={str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def finalize_stock_take(stock_take: StockTake):
        """
        Finalize a stock take by reconciling each stock take item with system stock.
        
        Steps:
        1. Fetch movements that occurred after counting started.
        2. Adjust counted quantity for movements.
        3. Compare to system quantity and compute variance.
        4. Post variance as a manual adjustment (never overwrite stock).
        5. Save item-level reconciliation data.
        6. Mark stock take as completed after all items reconciled.
        """

        # A stock take is an event. Each StockTakeItem corresponds to a product.
        for item in stock_take.items.select_related("product"):

            # Get movements that occurred after counting started for this product
            movements = StockTakeReconcialiationService.get_stock_item_movements_during_stock_take(
                stock_take=stock_take,
                stock_take_item=item
            )

            # Apply movements to the counted quantity to get adjusted quantity
            adjustment = StockTakeReconcialiationService.adjust_stocktake_item_quantity_for_movements(
                counted_quantity=item.quantity_counted,
                movements=movements
            )
            adjusted_quantity = adjustment["adjusted_quantity"]

            # Get current system quantity for this product in this branch
            system_quantity = ProductStockService.get_product_stock_quantity(
                product=item.product,
                company=stock_take.company,
                branch=stock_take.branch
            )

            # Compute variance (difference between reality and system)
            variance = adjusted_quantity - system_quantity

            # Post variance as a manual stock adjustment (if any)
            if variance != 0:
                ProductStockService.adjust_stock_manually(
                    product=item.product,
                    company=stock_take.company,
                    branch=stock_take.branch,
                    quantity_change=variance,
                    reason=f"Stock take {stock_take.reference_number}",
                    performed_by=stock_take.performed_by
                )

            # Save item-level reconciliation details
            item.adjusted_quantity = adjusted_quantity
            item.movement_breakdown = adjustment
            item.save(update_fields=["adjusted_quantity", "movement_breakdown"])

            logger.info(
                f"Stock take item finalized | Ref={stock_take.reference_number} | "
                f"Product={item.product.id} | "
                f"Counted={item.quantity_counted} | "
                f"Adjusted={adjusted_quantity} | "
                f"SystemBefore={system_quantity} | "
                f"VariancePosted={variance}"
            )

        # Mark the entire stock take as completed after all items reconciled
        stock_take.status = "completed"
        stock_take.completed_at = timezone.now()
        stock_take.save(update_fields=["status", "completed_at"])

        logger.info(
            f"Stock take completed | Ref={stock_take.reference_number} | "
            f"Items={stock_take.items.count()}"
        )

    

    @staticmethod
    def preview_stock_take(stock_take: StockTake):
        """
        Returns per-product stock take preview without touching system stock.

        Each row explains:
        - what was counted
        - what happened during the stock take
        - what the real quantity should be
        - what adjustment will be posted
        """

        preview = []

        for item in stock_take.items.select_related("product"):

            # 1. Get movements that happened while stock take was open
            movements = StockTakeReconcialiationService.get_stock_item_movements_during_stock_take(
                stock_take=stock_take,
                stock_take_item=item
            )

            # 2. Calculate how those movements affected the counted quantity
            adjustment = StockTakeReconcialiationService.adjust_stocktake_item_quantity_for_movements(
                counted_quantity=item.counted_quantity,
                movements=movements
            )

            adjusted_quantity = adjustment["adjusted_quantity"]

            # Remove adjusted_quantity from breakdown (we only want movement types there)
            movement_breakdown = adjustment.copy()
            movement_breakdown.pop("adjusted_quantity")

            # 3. Get current system stock
            system_quantity = ProductStockService.get_product_stock_quantity(
                product=item.product,
                company=stock_take.company,
                branch=stock_take.branch
            )

            # 4. Compute variance
            variance = adjusted_quantity - system_quantity

            preview.append({
                "product_id": item.product.id,
                "product_name": item.product.name,
                "system_quantity": system_quantity,
                "counted_quantity": item.counted_quantity,
                "adjusted_quantity": adjusted_quantity,
                "variance": variance,
                "movements": movement_breakdown,
            })

        return preview
