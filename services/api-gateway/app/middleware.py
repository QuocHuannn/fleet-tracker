"""Middleware utilities for API Gateway"""
from fastapi import Request
import uuid
from typing import Optional

def add_correlation_id(request: Request) -> str:
    """Add correlation ID to request"""
    # Check if correlation ID already exists in headers
    correlation_id = request.headers.get("x-correlation-id")
    
    # Generate new correlation ID if not provided
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    
    # Store in request state
    request.state.correlation_id = correlation_id
    
    return correlation_id