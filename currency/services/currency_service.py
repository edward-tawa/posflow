from django.db import transaction as db_transaction
from currency.models.currency_model import Currency
from loguru import logger



class CurrencyService:

    @staticmethod
    @db_transaction.atomic
    def create_currency(
        *,
        name: str,
        code: str,
        symbol: str,
        is_base_currency: bool,
        exchange_rate_to_base: float,
        is_active: bool = True,
    ) -> Currency:
        """
        Service method to create a new currency.
        """
        try:
            currency = Currency.objects.create(
                name=name,
                code=code,
                symbol=symbol,
                is_base_currency=is_base_currency,
                is_active=is_active,
            )
            logger.info(f"Currency created: {currency}")
            return currency
        except Exception as e:
            logger.exception("Error creating currency")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def update_currency(
        *,
        currency: Currency,
        name: str = None,
        code: str = None,
        symbol: str = None,
        is_base_currency: bool = None,
        exchange_rate_to_base: float = None,
        is_active: bool = None,
    ) -> Currency:
        """
        Service method to update an existing currency.
        """
        try:
            if name is not None:
                currency.name = name
            if code is not None:
                currency.code = code
            if symbol is not None:
                currency.symbol = symbol
            if is_base_currency is not None:
                currency.is_base_currency = is_base_currency
            if exchange_rate_to_base is not None:
                currency.exchange_rate_to_base = exchange_rate_to_base
            if is_active is not None:
                currency.is_active = is_active
            
            currency.save()
            logger.info(f"Currency updated: {currency}")
            return currency
        except Exception as e:
            logger.exception("Error updating currency")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def delete_currency(*, currency: Currency) -> None:
        """
        Service method to delete a currency.
        """
        try:
            currency.delete()
            logger.info(f"Currency deleted: {currency}")
        except Exception as e:
            logger.exception("Error deleting currency")
            raise
    

    @staticmethod
    def get_currency_by_code(*, code: str) -> Currency:
        """
        Service method to retrieve a currency by its code.
        """
        try:
            currency = Currency.objects.get(code=code)
            logger.info(f"Currency retrieved: {currency}")
            return currency
        except Currency.DoesNotExist:
            logger.warning(f"Currency with code {code} does not exist")
            return None
        except Exception as e:
            logger.exception("Error retrieving currency")
            raise

    

    @staticmethod
    def get_currency_by_name(*, name: str):
        """
        Service method to retrieve a currency by its name.
        """
        try:
            currency = Currency.objects.get(name=name)
            logger.info(f"Currency retrieved: {currency}")
            return currency
        except Currency.DoesNotExist:
            logger.warning(f"Currency with name {name} does not exist")
            return None
        except Exception as e:
            logger.exception("Error retrieving currency")
            raise
    
    @staticmethod
    def list_currencies(*, active_only=True):
        try:
            qs = Currency.objects.all()
            if active_only:
                qs = qs.filter(is_active=True)
            return qs.order_by('code')
        except Exception as e:
            logger.exception("Error listing currencies")
            raise

    
    @staticmethod
    def get_base_currency():
        try:
            return Currency.objects.get(is_base_currency=True)
        except Currency.DoesNotExist:
            logger.warning("No base currency set")
            return None
        except Exception as e:
            logger.exception("Error retrieving base currency")
            raise

    @staticmethod
    @db_transaction.atomic
    def set_base_currency(*, currency: Currency):
        try:
            # Reset previous base currency
            Currency.objects.filter(is_base_currency=True).update(is_base_currency=False)
            # Set new base
            currency.is_base_currency = True
            currency.save(update_fields=['is_base_currency'])
            logger.info(f"{currency.code} is now the base currency")
            return currency
        except Exception as e:
            logger.exception("Error setting base currency")
            raise

    
    @staticmethod
    def convert_amount(amount: float, from_currency: Currency, to_currency: Currency):
        try:
            if from_currency == to_currency:
                return amount
            # Convert to base first, then to target
            base_amount = amount / from_currency.exchange_rate_to_base
            return base_amount * to_currency.exchange_rate_to_base
        except Exception as e:
            logger.exception("Error converting amount between currencies")
            raise


