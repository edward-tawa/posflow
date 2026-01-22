from currency.services.currency_service import CurrencyService
from currency.models.currency_model import Currency


def set_base_currency_util(currency: Currency) -> Currency:
    """
    Utility function to set the base currency.
    """
    currency = CurrencyService.set_base_currency(currency=currency)
    return currency