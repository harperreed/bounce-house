# ABOUTME: Rate limiting middleware for spam protection
# ABOUTME: Prevents abuse by limiting requests per IP address with configurable windows

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict, Tuple
from collections import defaultdict


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_seconds: int = 3600):
        super().__init__(app)
        self.limits: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        
        # Skip rate limiting for non-submission endpoints
        if request.url.path != "/submit" or request.method != "POST":
            return await call_next(request)
        
        # Check rate limit
        count, window_start = self.limits[client_ip]
        now = time.time()
        
        # Reset window if expired
        if now - window_start > self.window_seconds:
            count = 0
            window_start = now
            
        if count >= self.max_requests:
            raise HTTPException(
                status_code=429, 
                detail=f"Too many requests. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
            )
            
        # Increment counter
        self.limits[client_ip] = (count + 1, window_start)
        
        return await call_next(request)
        
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers, preferring forwarded headers."""
        # Try various headers in order of preference
        ip_headers = ["x-forwarded-for", "x-real-ip", "cf-connecting-ip"]
        
        for header in ip_headers:
            if header in request.headers:
                # For X-Forwarded-For, take the first IP (original client)
                return request.headers[header].split(",")[0].strip()
                
        # Fall back to client host
        return request.client.host if request.client else "unknown"