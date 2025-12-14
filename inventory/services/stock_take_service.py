from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.services.product_stock_service import ProductStockService


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
            reference_number = StockTake.generate_reference_number()
            stock_take = StockTake.objects.create(
                company=company,
                branch=branch,
                quantity_counted=quantity_counted,
                performed_by=performed_by,
                reference_number=reference_number,
                notes=notes
            )
            logger.info(
                f"Stock take created: Company='{company.name}', Branch='{branch.name}', "
                f"Reference Number='{reference_number}', Quantity Counted={quantity_counted}, Performed By='{performed_by.username}'"
            )
            return stock_take

        except Exception as e:
            logger.error(
                f"Failed to create stock take: Company='{company.name}', Branch='{branch.name}', Error={str(e)}"
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
    def update_quantity_counted(stock_take: StockTake, new_quantity: int):
        """
        Updates the quantity counted in an existing stock take record.

        Args:
            stock_take (StockTake): The stock take record to update.
            new_quantity (int): The new quantity counted.
        Returns:
            StockTake: The updated stock take record.   
        """
        try:
            stock_take.quantity_counted = new_quantity
            stock_take.save()
            logger.info(
                f"Stock take quantity updated: Reference Number='{stock_take.reference_number}', New Quantity Counted={new_quantity}"
            )
            return stock_take

        except Exception as e:
            logger.error(
                f"Failed to update stock take quantity: Reference Number='{stock_take.reference_number}', Error={str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def list_stock_takes(company=None, branch=None, status=None, start_date=None, end_date=None):
        """
        Returns filtered stock takes.
        """
        qs = StockTake.objects.all()

        if company:
            qs = qs.filter(company=company)
        if branch:
            qs = qs.filter(branch=branch)
        if status:
            qs = qs.filter(status=status)
        if start_date and end_date:
            qs = qs.filter(created_at__range=[start_date, end_date])

        return qs.order_by("-created_at")
    


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
        Finalize a stock take and update actual product stock in the system.
        """
        try:
            ProductStockService.update_quantity(
                product=stock_take.product,
                branch=stock_take.branch,
                new_quantity=stock_take.quantity_counted
            )

            stock_take.status = "completed"
            stock_take.save()

            logger.info(
                f"Stock take finalized: Ref='{stock_take.reference_number}', Stock Updated to '{stock_take.quantity_counted}'"
            )
            return stock_take
        except Exception as e:
            logger.error(
                f"Failed to finalize stock take: Ref='{stock_take.reference_number}', Error={str(e)}"
            )
            raise


