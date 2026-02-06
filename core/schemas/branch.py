from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class BranchSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: str
    company: int
    code: Optional[str]
    address: str
    city: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    manager: Optional[int]
    is_active: bool
    disable: bool
    opening_date: Optional[date]
    notes: Optional[str]


