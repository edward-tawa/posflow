from django.db import transaction, models
from django.db.models import Q
from django.core.exceptions import ValidationError

from customers.models import Customer
from loguru import logger


class CustomerService:

    @staticmethod
    @transaction.atomic
    def create_customer(data):
        """
        Create a new customer with validation and business rules.
        """
        CustomerService._validate_unique_fields(data)
        try:
            customer = Customer.objects.create(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                email=data.get("email"),
                phone_number=data.get("phone_number"),
                company=data.get("company"),
                branch=data.get("branch"),
                address=data.get("address"),
                notes=data.get("notes"),
            )

            logger.info(f"Customer {customer.email} created successfully")
            return customer
        except Exception as e:
            logger.exception(f"Error creating customer: {e}")
            raise

    @staticmethod
    @transaction.atomic
    def update_customer(customer: Customer, data):
        try:
            CustomerService._validate_updated_fields(customer, data)

            for key, value in data.items():
                setattr(customer, key, value)

            customer.save()
            logger.info(f"Customer {customer.email} updated successfully")
            return customer
        except Exception as e:
            logger.exception(f"Error updating customer {customer.email if customer else 'unknown'}: {e}")
            raise

    @staticmethod
    @transaction.atomic
    def delete_customer(customer: Customer):
        try:
            customer.delete()
            logger.info(f"Customer {customer.email} deleted")
            return True
        except Exception as e:
            logger.exception(f"Error deleting customer {customer.email if customer else 'unknown'}: {e}")
            raise


    @staticmethod
    def get_customer_by_id(customer_id):
        try:
            customer = Customer.objects.filter(id=customer_id).first()
            if not customer:
                logger.warning(f"Customer with ID {customer_id} not found")
            return customer
        except Exception as e:
            logger.exception(f"Error fetching customer by ID {customer_id}: {e}")
            raise

    @staticmethod
    def get_customer_by_email(email):
        try:
            customer = Customer.objects.filter(email=email).first()
            if not customer:
                logger.warning(f"Customer with email {email} not found")
            return customer
        except Exception as e:
            logger.exception(f"Error fetching customer by email {email}: {e}")
            raise               
    @staticmethod
    def get_customer_by_phone(phone):
        try:
            customer = Customer.objects.filter(phone_number=phone).first()
            if not customer:
                logger.warning(f"Customer with phone number {phone} not found")
            return customer
        except Exception as e:
            logger.exception(f"Error fetching customer by phone number {phone}: {e}")
            raise

    @staticmethod
    def search_customers(company, query):
        """
        Search customers by name, email, or phone in a specific company.
        """
        return Customer.objects.filter(
            company=company
        ).filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        )

    # ====================================================
    # INTERNAL VALIDATION HELPERS
    # ====================================================

    @staticmethod
    def _validate_unique_fields(data):
        """
        Validate email and phone uniqueness on creation.
        """
        email = data.get("email")
        phone = data.get("phone_number")

        if email and Customer.objects.filter(email=email).exists():
            raise ValidationError(f"Email '{email}' is already in use.")

        if phone and Customer.objects.filter(phone_number=phone).exists():
            raise ValidationError(f"Phone '{phone}' is already in use.")

    @staticmethod
    def _validate_updated_fields(customer, data):
        """
        Validate uniqueness on update only if values change.
        """
        new_email = data.get("email")
        new_phone = data.get("phone_number")

        if new_email and new_email != customer.email:
            if Customer.objects.filter(email=new_email).exists():
                raise ValidationError(f"Email '{new_email}' is already in use.")

        if new_phone and new_phone != customer.phone_number:
            if Customer.objects.filter(phone_number=new_phone).exists():
                raise ValidationError(f"Phone '{new_phone}' is already in use.")







