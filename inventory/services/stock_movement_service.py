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

        # Optional inventory snapshot
        quantity_before: int | None = None,
        quantity_after: int | None = None,

        # Optional costing
        unit_cost=None,

        # Optional references
        sales_order=None,
        sales_invoice=None,
        sales_return=None,
        purchase_order=None,
        purchase_invoice=None,
        purchase_return=None,

        reason: str | None = None
    ) -> StockMovement:
        """
        Creates a stock movement record.
        Does NOT mutate actual stock levels.
        """

        try:
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
                "Stock movement created | "
                f"Product={product.name} | "
                f"Branch={branch.name} | "
                f"Type={movement_type} | "
                f"Qty={quantity}"
            )

            return stock_movement

        except Exception as e:
            logger.exception(
                "Failed to create stock movement | "
                f"Product={product.id} | Branch={branch.id}"
            )
            raise



    @staticmethod
    def get_stock_movements(
        *,
        company: Company,
        product: Product | None = None,
        branch: Branch | None = None,
        movement_type: str | None = None,
        start_date=None,
        end_date=None
    ):
        """
        Retrieve stock movements with flexible filters.
        """

        try:
            filters = {'company': company, 'branch': branch}

            if product:
                filters['product'] = product
            if movement_type:
                filters['movement_type'] = movement_type
            if start_date:
                filters['movement_date__gte'] = start_date
            if end_date:
                filters['movement_date__lte'] = end_date

            qs = (
                StockMovement.objects
                .filter(**filters)
                .select_related('product', 'branch')
                .order_by('-movement_date')
            )

            logger.info(f"Retrieved {qs.count()} stock movements")
            return qs

        except Exception as e:
            logger.exception("Failed to retrieve stock movements")
            raise


    @staticmethod
    @db_transaction.atomic
    def update_stock_movement(
        stock_movement: StockMovement,
        **kwargs
    ) -> StockMovement:
        """
        Update fields of an existing stock movement.
        Only allows updating certain fields.
        """

        ALLOWED_UPDATE_FIELDS = {
            "quantity",
            "movement_type",
            "unit_cost",
            "reason",
            "quantity_before",
            "quantity_after",
        }

        for field, value in kwargs.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(stock_movement, field, value)

        stock_movement.save()
        logger.info(f"Stock movement updated | id={stock_movement.id}")
        return stock_movement
    


    @staticmethod
    def get_stock_movement_by_movement_date(
        *,
        company: Company,
        movement_date
    ) -> StockMovement | None:
        """
        Retrieve a stock movement by its movement date within a company.
        """

        try:
            stock_movement = StockMovement.objects.filter(
                company=company,
                movement_date=movement_date
            ).first()

            if stock_movement:
                logger.info(
                    f"Retrieved stock movement | id={stock_movement.id} "
                    f"for movement_date={movement_date}"
                )
            else:
                logger.info(
                    f"No stock movement found for movement_date={movement_date}"
                )

            return stock_movement

        except Exception as e:
            logger.exception(
                f"Failed to retrieve stock movement for movement_date={movement_date}"
            )
            raise


    @staticmethod
    def get_stock_movement_by_date_range(
        *,
        company: Company,
        start_date,
        end_date
    ):
        """
        Retrieve stock movements within a date range for a company.
        """

        try:
            stock_movements = StockMovement.objects.filter(
                company=company,
                movement_date__gte=start_date,
                movement_date__lte=end_date
            ).order_by('-movement_date')

            logger.info(
                f"Retrieved {stock_movements.count()} stock movements "
                f"from {start_date} to {end_date}"
            )

            return stock_movements

        except Exception as e:
            logger.exception(
                f"Failed to retrieve stock movements from {start_date} to {end_date}"
            )
            raise


    
    @staticmethod
    def get_stock_movement_by_id(
        *,
        company: Company,
        stock_movement_id: int
    ) -> StockMovement | None:
        """
        Retrieve a stock movement by its ID within a company.
        """

        try:
            stock_movement = StockMovement.objects.filter(
                company=company,
                id=stock_movement_id
            ).first()

            if stock_movement:
                logger.info(
                    f"Retrieved stock movement | id={stock_movement.id}"
                )
            else:
                logger.info(
                    f"No stock movement found with id={stock_movement_id}"
                )

            return stock_movement

        except Exception as e:
            logger.exception(
                f"Failed to retrieve stock movement with id={stock_movement_id}"
            )
            raise

    

    @staticmethod
    def get_end_of_day_stock_movements(
        *,
        company: Company,
        branch: Branch,
        date
    ):
        """
        Retrieve all stock movements for a specific branch on a given date.
        """

        try:
            stock_movements = StockMovement.objects.filter(
                company=company,
                branch=branch,
                movement_date__date=date
            ).order_by('-movement_date')

            logger.info(
                f"Retrieved {stock_movements.count()} stock movements "
                f"for branch={branch.name} on date={date}"
            )

            return stock_movements

        except Exception as e:
            logger.exception(
                f"Failed to retrieve stock movements for branch={branch.name} on date={date}"
            )
            raise





    @staticmethod
    def get_product_stock_summary_per_day(
        *,
        company: Company,
        branch: Branch,
        date,
        product: Product | None = None
    ):
        """
        Returns a dictionary with stock totals and value per product for a given branch and date.
        Uses database queries instead of Python iteration.
        """
        # Base queryset for the date and branch
        qs = StockMovement.objects.filter(
            company=company,
            branch=branch,
            movement_date__date=date
        ).select_related('product', 'branch')

        if product:
            qs = qs.filter(product=product)

        # Aggregate total quantity and total value per product
        aggregation = qs.values('product_id', 'product__name').annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('unit_cost'), output_field=FloatField())
        )

        # Convert to dictionary keyed by product id
        summary = {
            item['product_id']: {
                "product_name": item['product__name'],
                "quantity": item['total_quantity'] or 0,
                "value": item['total_value'] or 0,
            }
            for item in aggregation
        }

        return summary


    @staticmethod
    def get_stock_movement_by_movement_type(
        *,
        company: Company,
        branch: Branch,
        movement_type: str
    ):
        """
        Returns stock movements filtered by movement_type (sale, purchase, adjustment, etc.)
        """

        try:
            stock_movements = StockMovement.objects.filter(
                company=company,
                branch=branch,
                movement_type=movement_type
            ).order_by('-movement_date')

            logger.info(
                f"Retrieved {stock_movements.count()} stock movements "
                f"of type={movement_type}"
            )

            return stock_movements

        except Exception as e:
            logger.exception(
                f"Failed to retrieve stock movements of type={movement_type}"
            )
            raise


    
    @staticmethod
    def get_current_stock(
        *,
        company: Company,
        branch: Branch,
        product: Product
    ) -> int:
        """
        Returns the current stock quantity of a product at a branch.
        """
        result = StockMovement.objects.filter(
            company=company,
            branch=branch,
            product=product
        ).aggregate(total=Sum('quantity'))

        return result['total'] or 0
    


    @staticmethod
    def get_current_stock_value(
        *,
        company: Company,
        branch: Branch,
        product: Product
    ) -> float:
        """
        Returns the total value of current stock of a product at a branch.
        """
        result = StockMovement.objects.filter(
            company=company,
            branch=branch,
            product=product
        ).aggregate(
            total_value=Sum(F('quantity') * F('unit_cost'), output_field=FloatField())
        )

        return result['total_value'] or 0.0
        
    

   

    @staticmethod
    def get_movements_during_stock_take(stock_take):
        """
        Return all stock movements for the product(s) in a stock take
        that occurred between stock_take.started_at and stock_take.ended_at (or now if not ended).
        """
        end_time = stock_take.ended_at or timezone.now()
        product_ids = stock_take.items.values_list("product_id", flat=True)
        stock_item_movements = StockMovement.objects.filter(
            company=stock_take.company,
            branch=stock_take.branch,
            product_id__in=product_ids,
            movement_date__gte=stock_take.started_at,
            movement_date__lte=end_time
        )
        return stock_item_movements
    

    @staticmethod
    def get_stock_item_movements_during_stock_take(
        stock_take,
        stock_take_item
    ):
        """
        Return all stock movements for a specific stock take item
        that occurred between stock_take.started_at and stock_take.ended_at (or now if not ended).
        """
        end_time = stock_take.ended_at or timezone.now()
        stock_item_movements = StockMovement.objects.filter(
            company=stock_take.company,
            branch=stock_take.branch,
            product=stock_take_item.product,
            movement_date__gte=stock_take.started_at,
            movement_date__lte=end_time
        )
        return stock_item_movements
