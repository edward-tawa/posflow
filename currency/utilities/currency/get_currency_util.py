from currency.services.currency_service import CurrencyService
from currency.models.currency_model import Currency




def get_currency_util(currency_name: str) -> Currency:
    """
    Utility function to retrieve a currency by its name.
    """
    currency = CurrencyService.get_currency_by_name(name=currency_name)
    return currency




def get_currency_util_by_code(currency_code: str) -> Currency:
    """
    Utility function to retrieve a currency by its code.
    """
    currency = CurrencyService.get_currency_by_code(code=currency_code)
    return currency