from inventory.models.product_stock_model import ProductStock
from inventory.models.stock_take_item_model import StockTakeItem
from django.db import models
from django.db import transaction as db_transaction
from loguru import logger



class ProductStockService:
    @staticmethod
    @db_transaction.atomic
    def adjust_stock(product, company, branch, quantity_change):
        """
        Adjust the stock level for a given product in a specific branch.
        Positive quantity_change increases stock, negative decreases stock.
        """
        try:
            product_stock, created = ProductStock.objects.get_or_create(
                product=product,
                company=company,
                branch=branch,
                defaults={'quantity': 0}
            )
            product_stock.quantity += quantity_change
            if product_stock.quantity < 0:
                raise ValueError("Stock quantity cannot be negative.")
            product_stock.save()
            logger.info(f"Adjusted stock for {product.name} in {branch.name} by {quantity_change}. New quantity: {product_stock.quantity}")
            return product_stock
        except Exception as e:
            logger.error(f"Error adjusting stock for {product.name} in {branch.name}: {str(e)}")
            raise
        
    @staticmethod
    @db_transaction.atomic
    def add_stock(product, company, branch, quantity):
        """
        Add stock for a given product in a specific branch.
        """
        return ProductStockService.adjust_stock(product, company, branch, quantity)
    

    @staticmethod
    @db_transaction.atomic
    def remove_stock(product, company, branch, quantity):
        """
        Remove stock for a given product in a specific branch.
        """
        return ProductStockService.adjust_stock(product, company, branch, -quantity)
    

    @staticmethod
    @db_transaction.atomic
    def check_product_stock(product, company, branch):
        """
        Check total stock level for a given product across all branches.
        """
        try:
            total_stock = ProductStock.objects.filter(product=product, company=company, branch=branch).aggregate(
                total_quantity=models.Sum('quantity')
            )['total_quantity'] or 0
            logger.info(f"Total stock for {product.name} is {total_stock}")
            return total_stock
        except Exception as e:
            logger.error(f"Error checking stock for {product.name}: {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def calculate_total_product_stock_value(product, branch):
        """
        Calculate the total stock value for a given product in a specific branch.
        Total Stock Value = Stock Quantity * Product Price
        """
        try:
            product_stock = ProductStock.objects.get(product=product, branch=branch)
            total_value = product_stock.quantity * product.price
            logger.info(f"Total stock value for {product.name} in {branch.name} is {total_value}")
            return total_value
        except ProductStock.DoesNotExist:
            logger.warning(f"No stock record found for {product.name} in {branch.name}. Returning value 0.")
            return 0
        except Exception as e:
            logger.error(f"Error calculating stock value for {product.name} in {branch.name}: {str(e)}")
            raise
    

