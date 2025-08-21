import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.system_metrics_service import system_metrics

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track API metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Record API call
        system_metrics.record_api_call()
        
        # Track response time
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate and record response time
            end_time = time.time()
            response_time = end_time - start_time
            system_metrics.record_response_time(response_time)
            
            # Add response time header for debugging
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            
            return response
            
        except Exception as e:
            # Still record response time even for errors
            end_time = time.time()
            response_time = end_time - start_time
            system_metrics.record_response_time(response_time)
            
            logger.error(f"[METRICS] Request failed after {response_time:.3f}s: {e}")
            raise
