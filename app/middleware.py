"""
Security middleware for the HighScore API
Includes rate limiting, security headers, and request logging
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime
import time
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Skip strict CSP for documentation and landing page (they need external resources and inline styles)
        is_docs_or_landing = request.url.path in ["/", "/docs", "/redoc", "/openapi.json"]
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy - relaxed for docs/landing, strict for API
        if is_docs_or_landing:
            # Allow inline styles and CDN resources for docs and landing page
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "connect-src 'self'"
            )
        else:
            # Strict CSP for API endpoints
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests for monitoring and debugging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        print(f"[{datetime.utcnow().isoformat()}] {method} {path} from {client_ip}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            status_code = response.status_code
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            print(f"[{datetime.utcnow().isoformat()}] {method} {path} - {status_code} ({process_time:.3f}s)")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            print(f"[{datetime.utcnow().isoformat()}] {method} {path} - ERROR: {str(e)} ({process_time:.3f}s)")
            raise


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size to prevent memory exhaustion attacks"""
    
    def __init__(self, app, max_request_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size is {self.max_request_size} bytes"
                )
        
        return await call_next(request)


class IPBlockingMiddleware(BaseHTTPMiddleware):
    """Block requests from blacklisted IPs"""
    
    def __init__(self, app, blacklist: set = None):
        super().__init__(app)
        self.blacklist = blacklist or set()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else None
        
        if client_ip and client_ip in self.blacklist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return await call_next(request)
