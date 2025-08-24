"""Standard response format for Fleet Tracker APIs"""
from typing import Any, Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime

class ApiResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

def success_response(data: Any = None, message: str = "Success", meta: Dict[str, Any] = None) -> ApiResponse:
    """Create successful response"""
    return ApiResponse(
        success=True,
        message=message,
        data=data,
        meta=meta
    )

def error_response(message: str, errors: List[str] = None, data: Any = None) -> ApiResponse:
    """Create error response"""
    return ApiResponse(
        success=False,
        message=message,
        errors=errors or [],
        data=data
    )

def validation_error_response(errors: List[str]) -> ApiResponse:
    """Create validation error response"""
    return ApiResponse(
        success=False,
        message="Validation failed",
        errors=errors
    )

class PaginatedResponse(BaseModel):
    """Paginated response format"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[Any], total: int, page: int, size: int) -> "PaginatedResponse":
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

def paginated_success_response(items: List[Any], total: int, page: int, size: int, message: str = "Success") -> ApiResponse:
    """Create paginated success response"""
    paginated_data = PaginatedResponse.create(items, total, page, size)
    return ApiResponse(
        success=True,
        message=message,
        data=paginated_data,
        meta={
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": paginated_data.pages
            }
        }
    )
