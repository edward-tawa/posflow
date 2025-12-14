from inventory.models.product_model import Product
from inventory.models.product_category_model import ProductCategory
from inventory.models.product_stock_model import ProductStock
from inventory.models.stock_take_item_model import StockTakeItem
from django.db import transaction as db_transaction
from django.http import StreamingHttpResponse
import csv
from io import StringIO
from django.db.models import Q
from loguru import logger


class ProductService:


    @staticmethod
    @db_transaction.atomic
    def create_product(company, name, description, price, product_category=None, stock_quantity=0):
        """
        Create a new product in the inventory.
        """
        try:
            product = Product.objects.create(
                company=company,
                name=name,
                description=description,
                price=price,
                product_category=product_category,
                stock_quantity=stock_quantity
            )
            return product
        except Exception as e:
            logger.exception(f"Error creating product {name} for Company {company.id}: {e}")
            raise e


    @staticmethod
    @db_transaction.atomic
    def update_product(product: Product, **kwargs):
        """
        Update an existing product's details.
        """
        try:
            for key, value in kwargs.items():
                setattr(product, key, value)
            product.save()
            return product
        except Exception as e:
            logger.exception(f"Error updating product {product.id if product else 'unknown'}: {e}")
            raise e
        
    
    @staticmethod
    @db_transaction.atomic
    def delete_product(product: Product):
        """
        Delete a product from the inventory.
        """
        try:
            product.delete()
            logger.info(f"Product {product.id} deleted successfully")
            return True
        except Exception as e:
            logger.exception(f"Error deleting product {product.id if product else 'unknown'}: {e}")
            raise e
    
    @staticmethod
    def get_product_by_id(product_id):
        """
        Retrieve a product by its ID.
        """
        try:
            product = Product.objects.get(id=product_id)
            return product
        except Product.DoesNotExist:
            logger.warning(f"Product with ID {product_id} does not exist")
            return None
        except Exception as e:
            logger.exception(f"Error retrieving product with ID {product_id}: {e}")
            raise e
    

    @staticmethod
    @db_transaction.atomic
    def adjust_product_quantity(product: Product, adjustment: int):
        """
        Adjust the stock quantity of a product.
        Positive adjustment increases stock, negative decreases stock.
        """
        try:
            product.stock_quantity += adjustment
            product.save()
            logger.info(f"Adjusted stock for Product {product.id} by {adjustment}. New quantity: {product.stock_quantity}")
            return product
        except Exception as e:
            logger.exception(f"Error adjusting stock for Product {product.id}: {e}")
            raise e
    
    @staticmethod
    @db_transaction.atomic
    def list_products_by_category(category: ProductCategory):
        """
        List all products in a given category.
        """
        try:
            products = Product.objects.filter(product_category=category)
            return products
        except Exception as e:
            logger.exception(f"Error listing products for Category {category.id if category else 'unknown'}: {e}")
            raise e
        
    @staticmethod
    @db_transaction.atomic
    def search_products(company, query):
        """
        Search products by name or description in a specific company.
        """
        try:
            products = Product.objects.filter(
                company=company
            ).filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            return products
        except Exception as e:
            logger.exception(f"Error searching products in Company {company.id} with query '{query}': {e}")
            raise e
    
    @staticmethod
    @db_transaction.atomic
    def bulk_create_products(company, product_data_list):
        """
        Bulk create products in the inventory.
        product_data_list should be a list of dictionaries with product fields.
        """
        try:
            products = [Product(company=company, **data) for data in product_data_list]
            Product.objects.bulk_create(products, batch_size=1000, returning=True)
            logger.info(f"Bulk created {len(products)} products for Company {company.id}")
            return products
        except Exception as e:
            logger.exception(f"Error bulk creating products for Company {company.id}: {e}")
            raise e
        
    @staticmethod
    @db_transaction.atomic
    def bulk_update_products(products, update_fields):
        """
        Bulk update products in the inventory.
        products should be a list of Product instances to update.
        update_fields should be a list of fields to update.
        """
        try:
            Product.objects.bulk_update(products, update_fields, batch_size=1000)
            logger.info(f"Bulk updated {len(products)} products")
            return products
        except Exception as e:
            logger.exception(f"Error bulk updating products: {e}")
            raise e
    

class ProductService:

    @staticmethod
    @db_transaction.atomic
    def bulk_import_products(company, csv_file):
        """
        Bulk import products from a CSV file.
        The CSV should have columns: name, description, price, sku, product_category_id, stock_quantity
        Skips invalid rows but logs them.
        """
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            products = []
            failed_rows = []

            existing_skus = set(
                Product.objects.filter(company=company).values_list('sku', flat=True)
            )

            for row_number, row in enumerate(reader, start=2):  # start=2 to account for header row
                try:
                    # Required fields
                    name = row.get('name')
                    sku = row.get('sku')
                    price = row.get('price')
                    stock_quantity = row.get('stock_quantity')

                    if not (name and sku and price and stock_quantity):
                        raise ValueError("Missing required field(s)")

                    # Check SKU uniqueness
                    if sku in existing_skus:
                        raise ValueError(f"SKU '{sku}' already exists")

                    # Convert numeric fields
                    price = float(price)
                    stock_quantity = int(stock_quantity)

                    # Category (optional)
                    product_category = None
                    category_id = row.get('product_category_id')
                    if category_id:
                        product_category = ProductCategory.objects.get(
                            id=category_id,
                            company=company
                        )

                    # Create product instance
                    product = Product(
                        company=company,
                        name=name,
                        sku=sku,
                        description=row.get('description', ''),
                        price=price,
                        product_category=product_category,
                        stock_quantity=stock_quantity
                    )
                    products.append(product)
                    existing_skus.add(sku)  # mark SKU as used

                except Exception as e:
                    logger.warning(f"Skipping row {row_number}: {e}")
                    failed_rows.append((row_number, row, str(e)))

            # Bulk create valid products
            Product.objects.bulk_create(products, batch_size=1000, returning=True)
            logger.info(f"Bulk imported {len(products)} products for Company {company.id}")
            if failed_rows:
                logger.info(f"Skipped {len(failed_rows)} invalid rows")

            return products, failed_rows

        except Exception as e:
            logger.exception(f"Error bulk importing products for Company {company.id}: {e}")
            raise e


    @staticmethod
    @db_transaction.atomic
    def bulk_export_products(company, branch):
        """
        Bulk export products to a CSV format using streaming.
        Returns a StreamingHttpResponse suitable for download.
        """
        
        try:
            # Generator that yields CSV rows
            def csv_generator():
                # Create a StringIO buffer for each row
                output = StringIO()
                writer = csv.writer(output)

                # Write header
                writer.writerow([
                    'id', 'name', 'description', 'price', 'sku',
                    'product_category_id', 'stock_quantity', 'created_at', 'updated_at'
                ])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

                # Stream product rows
                for product in Product.objects.filter(company=company, branch=branch).iterator():
                    writer.writerow([
                        product.id,
                        product.name,
                        product.description,
                        product.price,
                        product.sku,
                        product.product_category.id if product.product_category else '',
                        product.stock_quantity,
                        product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        product.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    ])
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)

            logger.info(f"Streaming CSV export for Company {company.id}")
            return StreamingHttpResponse(
                csv_generator(),
                content_type='text/csv'
            )

        except Exception as e:
            logger.exception(f"Error bulk exporting products for Company {company.id}: {e}")
            raise e
