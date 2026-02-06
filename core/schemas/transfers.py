from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class CashTransferSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    transfer: Optional[int]
    company: int
    source_branch_account: int
    destination_branch_account: int
    currency: int
    total_amount: Decimal
    notes: Optional[str]


class ProductTransferSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    transfer: int
    company: int
    notes: Optional[str]


class TransferSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    source_branch: int
    destination_branch: int
    reference_number: str
    transferred_by: Optional[int]
    received_by: Optional[int]
    sent_by: Optional[int]
    transfer_date: Optional[date]
    currency: int
    total_amount: Decimal
    notes: Optional[str]
    type: str
    status: str


class ProductTransferItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    transfer: int
    product_transfer: int
    company: int
    branch: int
    product: int
    quantity: int
    unit_price: Decimal


