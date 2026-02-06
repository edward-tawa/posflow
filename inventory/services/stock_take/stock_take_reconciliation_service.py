from inventory.models.stock_take_item_model import StockTakeItem
from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.models import StockMovement
from django.utils import timezone



class StockTakeReconcialiationService:

    @staticmethod
    @db_transaction.atomic
    def adjust_stocktake_item_quantity_for_movements(counted_quantity: int, movements: list[StockMovement]) -> dict:
        """
        Adjust a counted stocktake quantity based on stock movements that occurred after counting.
        Returns adjusted quantity and breakdown.
        """
        type_map = {
            "SALE": ("sold", -1),
            "TRANSFER_OUT": ("transferred_out", -1),
            "PURCHASE_RETURN": ("purchases_return", -1),
            "DAMAGE": ("damaged", -1),
            "WRITE_OFF": ("written_off", -1),
            "MANUAL_DECREASE": ("manually_decreased", -1),
            "PURCHASE": ("purchases", 1),
            "TRANSFER_IN": ("transferred_in", 1),
            "SALE_RETURN": ("sales_returns", 1),
            "MANUAL_INCREASE": ("manually_increased", 1),
        }

        counters = {name: 0 for name, _ in type_map.values()}
        adjusted_quantity = counted_quantity or 0

        for m in movements:
            if m.movement_type in type_map:
                key, direction = type_map[m.movement_type]
                counters[key] += m.quantity or 0
                adjusted_quantity += direction * (m.quantity or 0)

        return {"adjusted_quantity": adjusted_quantity, **counters}

    @staticmethod
    def track_stocktake_item_for_movements(stocktake: StockTake, stock_take_item: StockTakeItem):
        """
        Returns a dict of movement_type -> quantity moved for a stocktake item.
        Safe if started_at is None.
        """
        if stocktake.status != "open" or stock_take_item.stock_take != stocktake:
            return {}

        movement_date_gte = stock_take_item.stock_take.started_at or timezone.now()

        movements = StockMovement.objects.filter(
            product=stock_take_item.product,
            company=stock_take_item.stock_take.company,
            branch=stock_take_item.stock_take.branch,
            movement_date__gte=movement_date_gte,
        )

        movement_types = [
            "SALE", "TRANSFER_OUT", "PURCHASE_RETURN", "DAMAGE", "WRITE_OFF",
            "MANUAL_DECREASE", "PURCHASE", "TRANSFER_IN", "SALE_RETURN", "MANUAL_INCREASE"
        ]

        counters = {m_type: 0 for m_type in movement_types}
        for m in movements:
            counters[m.movement_type] = counters.get(m.movement_type, 0) + (m.quantity or 0)
        return counters

    @staticmethod
    def get_stock_item_movements_during_stock_take(stock_take: StockTake, stock_take_item: StockTakeItem):
        """
        Returns a queryset of stock movements for a stock take item after counting.
        Safe if started_at is None or stock take not open.
        """
        if stock_take.status != "open" or stock_take_item.stock_take != stock_take:
            return StockMovement.objects.none()

        movement_date_gte = stock_take_item.stock_take.started_at or timezone.now()

        return StockMovement.objects.filter(
            product=stock_take_item.product,
            company=stock_take_item.stock_take.company,
            branch=stock_take_item.stock_take.branch,
            movement_date__gte=movement_date_gte,
        )
