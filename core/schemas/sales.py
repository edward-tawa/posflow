from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class DeliveryNoteItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    delivery_note: Optional[int]
    product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class DeliveryNoteSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    customer: int
    sales_order: int
    delivery_number: str
    delivery_date: Optional[datetime]
    total_amount: Decimal
    status: str
    issued_by: Optional[int]
    notes: Optional[str]


class SaleSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    customer: int
    sales_invoice: Optional[int]
    sale_receipt: Optional[int]
    sale_date: Optional[datetime]
    payment_status: str
    total_amount: Decimal
    tax_amount: Decimal
    sale_type: str
    sale_number: str
    issued_by: Optional[int]
    notes: Optional[str]


class SalesInvoiceItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    sales_invoice: int
    product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class SalesInvoiceSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    customer: int
    sale: Optional[int]
    sales_order: Optional[int]
    receipt: Optional[int]
    invoice_number: str
    invoice_date: Optional[datetime]
    currency: int
    total_amount: Decimal
    discount_amount: Decimal
    status: str
    is_voided: bool
    void_reason: Optional[str]
    voided_at: Optional[datetime]
    issued_at: Optional[datetime]
    issued_by: Optional[int]
    notes: Optional[str]


class SalesOrderItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    sales_order: int
    product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class SalesOrderSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    customer: int
    order_number: str
    customer_name: str
    order_date: Optional[date]
    paid_at: Optional[datetime]
    dispatched_at: Optional[datetime]
    status: str
    currency: int
    total_amount: Decimal
    sales_person: Optional[int]
    notes: Optional[str]


class SalesQuotationItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    sales_quotation: int
    product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class SalesQuotationSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    quotation_number: str
    customer: int
    quotation_date: Optional[datetime]
    valid_until: date
    currency: int
    total_amount: Decimal
    status: str
    created_by: Optional[int]
    notes: Optional[str]


class SalesReceiptItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    sales_receipt: int
    product: int
    sale: Optional[int]
    sales_order: Optional[int]
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class SalesReceiptSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    sales_payment: Optional[int]
    branch: int
    customer: int
    sale: Optional[int]
    sales_order: Optional[int]
    receipt_number: str
    receipt_date: Optional[datetime]
    currency: int
    total_amount: Decimal
    is_voided: bool
    void_reason: Optional[str]
    voided_at: Optional[datetime]
    status: str
    issued_by: Optional[int]
    notes: Optional[str]


class SalesReturnItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    sales_return: int
    product: int
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal
    status: str


class SalesReturnSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    customer: int
    sales_order: int
    sale: Optional[int]
    return_number: str
    return_date: date
    currency: int
    total_amount: Decimal
    processed_by: Optional[int]
    notes: Optional[str]


