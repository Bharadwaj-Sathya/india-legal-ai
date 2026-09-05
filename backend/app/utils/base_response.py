from typing import Generic, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """
    A base class for API responses.

    This class standardizes API responses across the application by including key components:

    Attributes:
        data (Optional[T]): The actual data returned by the API, which can be of any type.
        success (bool): Indicates whether the API request was successful.
        message (Optional[str]): A message providing additional context about the response.
        error (Optional[str]): An error message if the request failed.

    Config:
        orm_mode (bool): Enables compatibility with ORM models for seamless conversion.
    """

    data: Optional[T] = None
    success: bool = True
    message: Optional[str] = None
    error: Optional[str] = None

    # Extensible metadata (pagination, request_id, etc.)
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata",
    )

    model_config = {
        "from_attributes": True,
        "extra": "allow",
    }
