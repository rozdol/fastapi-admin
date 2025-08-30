from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.endpoints.frontend import router as frontend_router
from app.core.exceptions import AdminAccessDeniedException
from fastapi.templating import Jinja2Templates
from app.core.auth import get_current_user
from app.core.database import (
    SQLiteBase, PostgresDB1Base, PostgresDB2Base,
    sqlite_engine, postgres_db1_engine, postgres_db2_engine
)
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables for all databases
    SQLiteBase.metadata.create_all(bind=sqlite_engine)
    PostgresDB1Base.metadata.create_all(bind=postgres_db1_engine)
    PostgresDB2Base.metadata.create_all(bind=postgres_db2_engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include frontend router
app.include_router(frontend_router)

# Initialize templates for error pages
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(AdminAccessDeniedException)
async def admin_access_denied_handler(request: Request, exc: AdminAccessDeniedException):
    """Handle admin access denied errors with a custom 404 page"""
    return templates.TemplateResponse("404.html", {
        "request": request,
        "error_type": "admin_access"
    })


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with custom 404 page for admin access"""
    if exc.status_code == 404:
        # Check if this is an admin access denied case
        user = get_current_user(request)
        if user and not user.get("is_superuser") and request.url.path.startswith("/admin"):
            return templates.TemplateResponse("404.html", {
                "request": request,
                "error_type": "admin_access"
            })
        else:
            return templates.TemplateResponse("404.html", {
                "request": request,
                "error_type": "not_found"
            })
    return None  # Let FastAPI handle other HTTP exceptions


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """Handle 404 errors with a custom page"""
    return templates.TemplateResponse("404.html", {
        "request": request,
        "error_type": "not_found"
    })


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
