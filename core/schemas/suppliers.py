from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class PurchaseItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    purchase: int
    product: int
    purchase_order_item: Optional[int]
    product_name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class PurchaseInvoiceItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    purchase_invoice: int
    purchase: Optional[int]
    product: int
    quantity: int
    unit_price: Decimal


class PurchaseInvoiceSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    purchase: Optional[int]
    supplier: int
    purchase_order: Optional[int]
    invoice_number: str
    invoice_date: Optional[datetime]
    balance: Decimal
    currency: int
    total_amount: Decimal
    issued_by: Optional[int]


class PurchaseSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    supplier: int
    purchase_order: Optional[int]
    purchase_invoice: Optional[int]
    supplier_receipt: Optional[int]
    purchase_date: Optional[datetime]
    payment_status: str
    currency: int
    total_amount: Decimal
    tax_amount: Decimal
    purchase_type: str
    purchase_number: str
    issued_by: Optional[int]
    notes: Optional[str]


class SupplierSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: Optional[int]
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    notes: Optional[str]


class PurchaseOrderItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    purchase_order: int
    product: int
    product_category: Optional[int]
    quantity: int
    unit_price: Decimal


class PurchaseOrderSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    supplier: int
    quantity_ordered: int
    order_date: Optional[date]
    delivery_date: Optional[date]
    currency: int
    total_amount: Decimal
    status: str
    reference_number: Optional[str]
    notes: Optional[str]


class PurchasePaymentAllocationSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    supplier: int
    purchase_payment: int
    purchase_invoice: int
    allocation_number: str
    allocation_date: Optional[datetime]
    currency: int
    total_allocated_amount: Decimal
    allocated_by: Optional[int]


class PurchaseReturnItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    purchase_return: int
    product: int
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal


class PurchaseReturnSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    supplier: Optional[int]
    purchase_order: int
    purchase: Optional[int]
    purchase_return_number: str
    return_date: Optional[datetime]
    issued_by: Optional[int]
    currency: int
    total_amount: Decimal


class SupplierCreditNoteItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    supplier_credit_note: int
    description: str
    quantity: int
    unit_price: Decimal


class SupplierCreditNoteSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    supplier: int
    credit_note_number: str
    credit_date: Optional[datetime]
    issued_by: Optional[int]
    currency: int
    total_amount: Decimal


class SupplierDebitNoteItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    supplier_debit_note: int
    description: str
    quantity: int
    unit_price: Decimal


class SupplierDebitNoteSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    supplier: int
    debit_note_number: str
    debit_date: Optional[datetime]
    issued_by: Optional[int]
    currency: int
    total_amount: Decimal


class SupplierReceiptItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    receipt: int
    product: int
    product_name: str
    quantity_received: int
    unit_price: Decimal
    tax_rate: Decimal


class SupplierReceiptSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    supplier_payment: Optional[int]
    branch: int
    supplier: int
    purchase_order: Optional[int]
    purchase_invoice: Optional[int]
    receipt_number: str
    receipt_date: Optional[datetime]
    currency: int
    total_amount: Decimal
    is_voided: bool
    void_reason: Optional[str]
    voided_at: Optional[datetime]
    status: str
    received_by: Optional[int]
    notes: Optional[str]


