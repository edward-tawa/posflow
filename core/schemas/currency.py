from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class CurrencySchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    code: str
    name: str
    symbol: str
    is_base_currency: bool
    exchange_rate_to_base: Decimal
    is_active: bool


