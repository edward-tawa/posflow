from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class ProductCategorySchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: Optional[int]
    name: str
    description: Optional[str]


class ProductSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    name: str
    description: str
    unit_price: Decimal
    currency: int
    product_category: Optional[int]
    stock: int
    sku: Optional[str]
    is_stock_take_item: bool


class ProductStockSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    product: int
    branch: int
    quantity: int
    reorder_level: int
    reorder_quantity: int


class StockAdjustmentSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    stock_take: int
    product: int
    quantity_before: int
    quantity_after: int
    adjustment_quantity: int
    reason: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]


class StockMovementSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    product: int
    sales_order: Optional[int]
    sales_return: Optional[int]
    sales_invoice: Optional[int]
    purchase_order: Optional[int]
    purchase_return: Optional[int]
    purchase_invoice: Optional[int]
    quantity_before: Optional[int]
    quantity_after: Optional[int]
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    movement_type: str
    quantity: int
    reason: Optional[str]
    reference_number: str


class StockTakeApprovalSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    stock_take: int
    approved_by: Optional[int]
    comment: Optional[str]


class StockTakeSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    quantity_counted: int
    performed_by: Optional[int]
    stock_take_date: Optional[datetime]
    status: str
    reference_number: Optional[str]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    is_approved: bool
    is_finalized: bool
    approved_by: Optional[int]
    rejected_by: Optional[int]
    rejection_reason: Optional[str]
    notes: Optional[str]
    total_counted_value: Decimal
    total_variance_value: Decimal


class StockTakeItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    stock_take: int
    product: int
    expected_quantity: int
    counted_quantity: int
    adjusted_quantity: Optional[float]
    movement_breakdown: Optional[dict]
    confirmed: bool


class StockWriteOffSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    reference: str
    reason: str
    notes: Optional[str]
    approved_by: Optional[int]
    status: str


class StockWriteOffItemSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    write_off: int
    product: int
    quantity: Decimal


