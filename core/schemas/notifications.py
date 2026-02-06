from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

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


