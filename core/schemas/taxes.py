from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class FiscalDeviceSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    device_name: str
    device_serial_number: str
    device_type: str
    is_active: bool


class FiscalDocumentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    device: Optional[int]
    content_type: int
    object_id: str
    fiscal_code: Optional[str]
    qr_code: Optional[str]
    raw_response: Optional[dict]
    is_fiscalized: bool
    source_document: Any


class FiscalInvoiceItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    fiscal_invoice: int
    sale_item: Optional[int]
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal


class FiscalInvoiceSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    device: Optional[int]
    sale: int
    invoice_number: str
    total_amount: Decimal
    total_tax: Decimal
    is_fiscalized: bool


class FiscalisationResponseSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    fiscal_invoice: int
    response_code: str
    response_message: str
    fiscal_code: Optional[str]
    qr_code: Optional[str]
    raw_response: dict


