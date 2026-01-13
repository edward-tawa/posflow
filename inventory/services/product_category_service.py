from inventory.models.product_category_model import ProductCategory
from inventory.models.product_model import Product
from loguru import logger
from django.db import transaction as db_transaction

class ProductCategoryService:

    @staticmethod
    @db_transaction.atomic
    def create_product_category(company, name, description):
        """
        Creates a new product category.

        Args:
            company: The company to which the category belongs.
            name (str): The name of the product category.
            description (str): A description of the product category.

        Returns:
            ProductCategory: The created product category.
        """
        try:
            product_category = ProductCategory.objects.create(
                company=company,
                name=name,
                description=description
            )
            logger.info(f"Product category created: Company='{company.name}', Name='{name}'")
            return product_category

        except Exception as e:
            logger.error(f"Failed to create product category: Company='{company.name}', Name='{name}', Error={str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def update_product_category(category: ProductCategory, name: str = None, description: str = None):
        """
        Updates an existing product category safely, preventing unique constraint violations.
        """
        try:
            if name is not None:
                # Check for existing category with the same name in the same company + branch
                exists = ProductCategory.objects.filter(
                    company=category.company,
                    branch=category.branch,
                    name=name
                ).exclude(id=category.id).exists()

                if exists:
                    raise ValueError(f"A category with the name '{name}' already exists for this company/branch.")

                category.name = name

            if description is not None:
                category.description = description

            category.save()
            logger.info(f"Product category updated: ID='{category.id}', Name='{category.name}'")
            return category

        except ValueError as ve:
            logger.error(f"Update failed due to uniqueness violation: {str(ve)}")
            raise

        except Exception as e:
            logger.error(f"Failed to update product category: ID='{category.id}', Error={str(e)}")
            raise

    

    @staticmethod
    @db_transaction.atomic
    def delete_product_category(category: ProductCategory):
        """
        Deletes a product category.

        Args:
            category (ProductCategory): The product category to delete.

        Returns:
            None
        """
        try:
            category_id = category.id
            category.delete()
            logger.info(f"Product category deleted: ID='{category_id}'")

        except Exception as e:
            logger.error(f"Failed to delete product category: ID='{category.id}', Error={str(e)}")
            raise

    
    @staticmethod
    @db_transaction.atomic
    def add_product_to_category(product: Product, category: ProductCategory):
        """
        Assigns a product to a category safely.
        """
        if product.company != category.company:
            raise ValueError("Product and category must belong to the same company")
        if category.branch and product.branch != category.branch:
            raise ValueError("Product and category branch mismatch")

        product.product_category = category
        product.save(update_fields=["product_category"])
        logger.info(f"Product '{product.name}' added to category '{category.name}'")
        return product


    @staticmethod
    @db_transaction.atomic
    def get_product_category_by_id(category_id: int):
        """
        Retrieves a product category by its ID.

        Args:
            category_id (int): The ID of the product category.
        Returns:
            ProductCategory: The retrieved product category.
        """
        try:
            category = ProductCategory.objects.get(id=category_id)
            logger.info(f"Product category retrieved: ID='{category_id}'")
            return category

        except ProductCategory.DoesNotExist:
            logger.error(f"Product category not found: ID='{category_id}'")
            raise

        except Exception as e:
            logger.error(f"Failed to retrieve product category: ID='{category_id}', Error={str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def list_product_categories(company,branch):
        """
        Lists all product categories for a given company and branch.

        Args:
            company: The company to which the categories belong.
            branch: The branch to which the categories belong.
        Returns:
            QuerySet: A queryset of product categories.
        """
        try:
            categories = ProductCategory.objects.filter(company=company,branch=branch).order_by('name')
            logger.info(f"Product categories listed for Company='{company.name}', Branch='{branch.name}'")
            return categories

        except Exception as e:
            logger.error(f"Failed to list product categories: Company='{company.name}', Branch='{branch.name}', Error={str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def search_product_categories(company, branch, search_term: str):
        """
        Searches product categories by name for a given company and branch.

        Args:
            company: The company to which the categories belong.
            branch: The branch to which the categories belong.
            search_term (str): The term to search in category names.
        Returns:
            QuerySet: A queryset of matching product categories.
        """
        try:
            categories = ProductCategory.objects.filter(
                company=company,
                branch=branch,
                name__icontains=search_term
            ).order_by('name')
            logger.info(f"Product categories searched for Company='{company.name}', Branch='{branch.name}', Search Term='{search_term}'")
            return categories

        except Exception as e:
            logger.error(f"Failed to search product categories: Company='{company.name}', Branch='{branch.name}', Search Term='{search_term}', Error={str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def get_product_category(product: Product, company, branch):
        """
        Retrieves the product category for a given product for a specific company and branch.

        Args:
            product (Product): The product whose category is to be retrieved.
            company: The company to which the product belongs.
            branch: The branch to which the product belongs.
        Returns:
            ProductCategory: The product category of the product.
        """        
        try:
            category = ProductCategory.objects.get(products__id=product.id, company=company, branch=branch)
            logger.info(f"Product category retrieved for Product='{product.name}', Company='{company.name}', Branch='{branch.name}'")
            return category

        except ProductCategory.DoesNotExist:
            logger.error(f"Product category not found for Product='{product.name}', Company='{company.name}', Branch='{branch.name}'")
            raise

        except Exception as e:
            logger.error(f"Failed to retrieve product category for Product='{product.name}', Company='{company.name}', Branch='{branch.name}', Error={str(e)}")
            raise