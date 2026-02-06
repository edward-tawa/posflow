from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class TransactionSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    customer: Optional[int]
    supplier: Optional[int]
    debit_account: int
    credit_account: int
    transaction_type: str
    transaction_direction: str
    transaction_category: str
    transaction_number: str
    payment_method: str
    reversal_applied: Optional[bool]
    status: str
    reference_model: Optional[str]
    reference_id: Optional[int]
    transaction_date: Optional[datetime]
    currency: int
    total_amount: Decimal


class TransactionItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    transaction: int
    product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal
    total_price: Decimal


