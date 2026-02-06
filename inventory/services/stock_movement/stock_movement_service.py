from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.product_model import Product
from inventory.models.stock_movement_model import StockMovement
from company.models import Company
from branch.models import Branch
from collections import defaultdict
from django.db.models import Sum, F, Q, FloatField
from django.utils import timezone



class StockMovementService:

    @staticmethod
    @db_transaction.atomic
    def create_stock_movement(
        *,
        company: Company,
        branch: Branch,
        product: Product,
        quantity: int,
        movement_type: str,
        quantity_before: int | None = None,
        quantity_after: int | None = None,
        unit_cost=None,
        sales_order=None,
        sales_invoice=None,
        sales_return=None,
        purchase_order=None,
        purchase_invoice=None,
        purchase_return=None,
        reason: str | None = None
    ) -> StockMovement:
        try:
            # TODO: Consider adding more specific exception handling here in the future
            stock_movement = StockMovement.objects.create(
                company=company,
                branch=branch,
                product=product,
                quantity=quantity,
                movement_type=movement_type,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                unit_cost=unit_cost,
                sales_order=sales_order,
                sales_invoice=sales_invoice,
                sales_return=sales_return,
                purchase_order=purchase_order,
                purchase_invoice=purchase_invoice,
                purchase_return=purchase_return,
                reason=reason,
            )
            logger.info(
                f"Stock movement created | Product={product.name} | "
                f"Branch={branch.name} | Type={movement_type} | Qty={quantity}"
            )
            return stock_movement
        except Exception as e:
            logger.exception(
                f"Failed to create stock movement | Product={product.id} | Branch={branch.id}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def update_stock_movement(
        stock_movement: StockMovement,
        **kwargs
    ) -> StockMovement:
        ALLOWED_UPDATE_FIELDS = {
            "quantity", "movement_type", "unit_cost",
            "reason", "quantity_before", "quantity_after"
        }
        for field, value in kwargs.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(stock_movement, field, value)
        stock_movement.save()
        logger.info(f"Stock movement updated | id={stock_movement.id}")
        return stock_movement

    @staticmethod
    def get_stock_movements(
        *,
        company: Company,
        stock_movement_id: int | None = None,
        product: Product | None = None,
        branch: Branch | None = None,
        movement_type: str | None = None,
        start_date=None,
        end_date=None,
        movement_date=None,
        order_desc: bool = True
    ):
        """
        Flexible query for stock movements.
        All filters are optional except company.
        """
        try:
            filters = {"company": company}

            if stock_movement_id is not None:
                filters["id"] = stock_movement_id
            if product is not None:
                filters["product"] = product
            if branch is not None:
                filters["branch"] = branch
            if movement_type is not None:
                filters["movement_type"] = movement_type
            if start_date is not None:
                filters["movement_date__gte"] = start_date
            if end_date is not None:
                filters["movement_date__lte"] = end_date
            if movement_date is not None:
                filters["movement_date"] = movement_date

            qs = StockMovement.objects.filter(**filters).select_related("product", "branch")
            if order_desc:
                qs = qs.order_by("-movement_date")
            else:
                qs = qs.order_by("movement_date")

            logger.info(f"Retrieved {qs.count()} stock movements with filters: {filters}")
            return qs

        except Exception as e:
            logger.exception("Failed to retrieve stock movements")
            raise

    

    @staticmethod
    def get_stock_movement_by_id(company: Company, stock_movement_id: int):
        """
        Retrieves a single stock movement by its ID.
        """
        # TODO : Consider adding more specific exception handling here in the future
        # TODO : Consider adding caching mechanism for frequently accessed stock movements
        try:
            return StockMovementService.get_stock_movements(
                company=company,
                stock_movement_id=stock_movement_id
            ).first()
        except Exception as e:
            logger.exception(f"Failed to retrieve stock movement with ID: {stock_movement_id}")
            raise

    @staticmethod
    def get_end_of_day_stock_movements(company: Company, branch: Branch, date):
        """
        Retrieves all stock movements for a specific branch on a given date.
        """

        try:
            return StockMovementService.get_stock_movements(
                company=company,
                branch=branch,
                start_date=date,
                end_date=date
            )
        except Exception as e:
            logger.exception(f"Failed to retrieve end of day stock movements for branch ID: {branch.id} on date: {date}")
            raise