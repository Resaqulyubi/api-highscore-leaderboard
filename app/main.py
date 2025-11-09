from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .config import settings
from .database import init_db
from .routes import router
from .rate_limiter import limiter, rate_limit_exceeded_handler
from .middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    RequestSizeLimitMiddleware,
    IPBlockingMiddleware
)
from slowapi.errors import RateLimitExceeded

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Configure CORS
origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware (order matters!)
if settings.enable_security_headers:
    app.add_middleware(SecurityHeadersMiddleware)

if settings.enable_request_logging:
    app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(RequestSizeLimitMiddleware, max_request_size=settings.max_request_size)
app.add_middleware(IPBlockingMiddleware, blacklist=set())  # Add IPs to blacklist as needed

# Add rate limiting
if settings.enable_rate_limiting:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Include routers
app.include_router(router)


# Global exception handler for better error messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    print(f"Unhandled exception: {str(exc)}")
    import traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "type": "internal_error"
        }
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("=" * 60)
    print("Database initialized")
    print(f"HighScore API v{settings.api_version} is running!")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print("")
    print("Security Features Enabled:")
    print(f"  - Rate Limiting: {settings.enable_rate_limiting}")
    print(f"  - Security Headers: {settings.enable_security_headers}")
    print(f"  - Request Logging: {settings.enable_request_logging}")
    print(f"  - Request Size Limit: {settings.max_request_size} bytes")
    print("=" * 60)


@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """Serve the landing page"""
    html_file = Path(__file__).parent.parent / "static" / "index.html"
    
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
    else:
        # Fallback JSON response if HTML file doesn't exist
        return {
            "message": "Welcome to HighScore API!",
            "version": settings.api_version,
            "docs": "/docs",
            "redoc": "/redoc",
            "github": "https://github.com/Resaqulyubi/api-highscore-leaderboard",
            "support": "https://buymeacoffee.com/qulyubi",
            "security": {
                "rate_limiting": settings.enable_rate_limiting,
                "security_headers": settings.enable_security_headers
            }
        }
