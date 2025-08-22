# API Gateway Middleware
# Rate limiting, logging và security middleware

from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
import json
from typing import Dict, Any
import redis
from .config import settings

logger = logging.getLogger(__name__)

# Redis client for rate limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        if not redis_client:
            return await call_next(request)
            
        # Get client identifier (IP hoặc user ID)
        client_id = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Extract user ID from JWT token if available
            # TODO: Implement JWT user extraction
            pass
            
        # Rate limiting key
        rate_limit_key = f"rate_limit:{client_id}:{int(time.time() // 60)}"  # Per minute
        
        try:
            # Get current request count
            current_requests = redis_client.get(rate_limit_key)
            if current_requests is None:
                current_requests = 0
            else:
                current_requests = int(current_requests)
            
            # Check rate limit
            if current_requests >= settings.RATE_LIMIT_REQUESTS_PER_MINUTE:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": "Too many requests per minute",
                        "retry_after": 60
                    }
                )
            
            # Increment counter
            redis_client.incr(rate_limit_key)
            redis_client.expire(rate_limit_key, 60)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
            response.headers["X-RateLimit-Remaining"] = str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE - current_requests - 1)
            response.headers["X-RateLimit-Reset"] = str(int(time.time() // 60 + 1) * 60)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/Response logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"📨 {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security headers middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
