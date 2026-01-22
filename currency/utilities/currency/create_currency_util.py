from currency.services.currency_service import CurrencyService
from currency.models.currency_model import Currency


def create_currency_util(
    *,
    name: str,
    code: str,
    symbol: str,
    is_base_currency: bool,
    exchange_rate_to_base: float,
    is_active: bool = True,
) -> Currency:
    """
    Utility function to create a new currency.
    """
    currency = CurrencyService.create_currency(
        name=name,
        code=code,
        symbol=symbol,
        is_base_currency=is_base_currency,
        exchange_rate_to_base=exchange_rate_to_base,
        is_active=is_active,
    )
    return currency