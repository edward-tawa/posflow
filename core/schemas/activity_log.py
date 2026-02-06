from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

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


