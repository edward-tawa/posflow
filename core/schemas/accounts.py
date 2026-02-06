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


