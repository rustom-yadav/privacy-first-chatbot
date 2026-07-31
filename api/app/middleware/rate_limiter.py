"""
Rate limiting configuration using slowapi.

The limiter instance is created here and imported by:
- Routes: to decorate endpoints with @limiter.limit()
- main.py: to register with the FastAPI app

Rate limits are configured via settings (RATE_LIMIT_CHAT, RATE_LIMIT_UPLOAD).
Uses client IP address as the rate limit key (no login required).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function uses client IP — works without authentication
limiter = Limiter(key_func=get_remote_address)
