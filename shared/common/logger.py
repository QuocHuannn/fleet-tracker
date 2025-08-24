import logging
import sys
from typing import Optional
from datetime import datetime

class ServiceLogger:
    """Centralized logging utility for microservices"""
    
    @staticmethod
    def get_logger(service_name: str, level: str = "INFO") -> logging.Logger:
        """Get configured logger for a service"""
        logger = logging.getLogger(service_name)
        
        if logger.handlers:
            return logger
            
        # Set log level
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatter with service name and correlation ID support
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        return logger

def log_request(service_name: str, method: str, path: str, user_id: Optional[str] = None):
    """Log incoming request"""
    logger = ServiceLogger.get_logger(service_name)
    user_info = f" [User: {user_id}]" if user_id else ""
    logger.info(f"Request: {method} {path}{user_info}")

def log_response(service_name: str, path: str, status_code: int, duration_ms: float):
    """Log outgoing response"""
    logger = ServiceLogger.get_logger(service_name)
    logger.info(f"Response: {path} - {status_code} ({duration_ms:.2f}ms)")

def log_service_call(service_name: str, target_service: str, operation: str):
    """Log service-to-service calls"""
    logger = ServiceLogger.get_logger(service_name)
    logger.info(f"Service call: {service_name} -> {target_service}: {operation}")
