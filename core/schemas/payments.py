from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class ExpenseSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    expense_number: str
    expense_date: Optional[datetime]
    payment: Optional[int]
    status: str
    category: str
    currency: int
    total_amount: Decimal
    total_amount_paid: Decimal
    description: Optional[str]
    incurred_by: Optional[int]


class PaymentAllocationSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    allocated_to_content_type: int
    allocated_to_object_id: int
    allocation_number: str
    allocation_date: Optional[datetime]
    currency: int
    total_amount_allocated: Decimal
    allocated_to: Any


class PaymentMethodSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    is_active: bool
    payment_method_name: str
    payment_method_code: str


class PaymentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    paid_by: Optional[int]
    payment_direction: str
    payment_number: str
    payment_date: Optional[datetime]
    currency: int
    total_amount: Decimal
    status: str
    payment_method: str
    reference_model: Optional[str]
    reference_id: Optional[int]


class PaymentReceiptItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    payment_receipt: int
    description: Optional[str]
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class PaymentReceiptSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    receipt_number: str
    receipt_date: Optional[datetime]
    currency: int
    total_amount: Decimal
    issued_by: Optional[int]


class RefundSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    refund_number: str
    refund_date: Optional[datetime]
    currency: int
    total_amount: Decimal
    reason: str
    processed_by: Optional[int]
    notes: Optional[str]


class SalesPaymentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    sales_order: Optional[int]
    sales_invoice: Optional[int]
    sales_receipt: Optional[int]
    payment: int
    payment_method: int
    received_by: Optional[int]


class ExpensePaymentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    payment_method: int
    expense: int
    issued_by: Optional[int]


class PurchasePaymentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    payment_method: int
    purchase_order: Optional[int]
    purchase: Optional[int]
    purchase_invoice: Optional[int]
    issued_by: Optional[int]


class RefundPaymentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    payment_method: int
    refund: int
    processed_by: Optional[int]


class PaymentPlanSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    payment: int
    name: str
    requires_deposit: bool
    deposit_percentage: Optional[Decimal]
    max_duration_days: Optional[int]
    valid_from: datetime
    valid_until: Optional[datetime]
    reference_number: str
    is_active: bool


