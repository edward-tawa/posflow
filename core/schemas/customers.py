from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class CustomerBranchHistorySchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    branch: int
    customer: int
    last_visited: Optional[datetime]


class CustomerSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company: int
    branch: int
    address: Optional[str]
    notes: Optional[str]
    last_purchase_date: Optional[datetime]


