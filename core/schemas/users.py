from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

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


