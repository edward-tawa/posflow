from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

class AccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: str
    company: int
    branch: int
    account_number: str
    account_type: str
    currency: int
    balance: Decimal
    is_active: bool
    is_frozen: bool


class BankAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    branch: Optional[int]
    bank_name: str


class BranchAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    company: int
    branch: int
    account: int
    is_primary: bool


class CashAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    branch: Optional[int]


class CustomerAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    customer: int
    account: int
    branch: int
    credit_limit: Decimal


class EmployeeAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    employee: int
    account: int
    branch: int
    is_primary: bool


class ExpenseAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    branch: Optional[int]
    expense: int
    paid_by: Optional[int]


class LoanAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    loan: int
    account: int
    branch: int
    is_primary: bool


class PurchasesAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    branch: Optional[int]
    supplier: Optional[int]
    recipient_person: Optional[int]


class PurchasesReturnsAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    branch: Optional[int]
    supplier: Optional[int]
    return_person: Optional[int]


class SalesAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    company: int
    branch: Optional[int]
    sales_person: Optional[int]


class SalesReturnsAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    account: int
    branch: Optional[int]
    customer: Optional[int]
    sales_person: Optional[int]



class SupplierAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    supplier: int
    account: int
    company: Optional[int]
    branch: int
    is_primary: bool



class WriteOffAccountSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    write_off: int
    company: Optional[int]
    branch: Optional[int]
    account: int
    product: Optional[int]
    account_name: Optional[str]
    amount: Decimal





class ActivityLogSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user: Optional[int]
    action: str
    content_type: Optional[int]
    object_id: Optional[int]
    description: str
    metadata: Optional[dict]
    content_object: Any





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





class CompanySchema(Schema):
    id: Optional[int]
    password: str
    last_login: Optional[datetime]
    is_superuser: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    name: str
    email: str
    website: Optional[str]
    logo: Optional[Any]
    address: str
    phone_number: str
    is_active: bool
    is_staff: bool
    groups: Optional[list[int]]
    user_permissions: Optional[list[int]]





class CurrencySchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    code: str
    name: str
    symbol: str
    is_base_currency: bool
    exchange_rate_to_base: Decimal
    is_active: bool





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





class NotificationSchema(Schema):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    title: str
    message: str
    notification_from_content_type: Optional[int]
    notification_from_object_id: Optional[int]
    notification_to: int
    is_read: bool
    status: str
    notification_from: Any





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





class UserSchema(Schema):
    id: Optional[int]
    password: str
    last_login: Optional[datetime]
    is_superuser: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    username: str
    first_name: str
    last_name: Optional[str]
    email: str
    company: int
    branch: Optional[int]
    role: str
    is_active: bool
    is_staff: bool
    groups: Optional[list[int]]
    user_permissions: Optional[list[int]]




