from pydantic import BaseModel, ConfigDict

class Schema(BaseModel):
    """
    Base schema for describing pure data shape.
    Think: dataclass + validation.
    """
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
