"""
Rate limiting for the HighScore API
Prevents abuse and DoS attacks
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail
        },
        headers={"Retry-After": str(exc.detail)}
    )


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "create_game": "5/hour",      # Creating games is limited
    "submit_score": "100/minute",  # Allow many score submissions
    "get_leaderboard": "60/minute", # Generous limit for leaderboard queries
    "player_stats": "60/minute",   # Same for stats
    "health": "100/minute",        # Health checks can be frequent
    "default": "100/minute"        # Default for other endpoints
}
