from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class LoanSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    borrower: int
    loan_amount: Decimal
    interest_rate: Decimal
    start_date: date
    end_date: date
    issued_by: Optional[int]
    is_active: bool
    notes: Optional[str]


