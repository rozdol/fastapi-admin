from typing import List
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, require_auth, require_admin
from app.services.user_service import UserService
from app.services.settings_service import SettingsService
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page"""
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Register page"""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/auth/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email, password)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email/username or password"
        })
    
    # Check if user is activated
    if not user.is_active:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please check your email and activate your account before logging in"
        })
    
    # Store user in session
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }
    
    return RedirectResponse(url="/", status_code=303)


@router.post("/auth/register", response_class=HTMLResponse)
async def register_form(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    """Handle register form submission"""
    from app.services.auth_service import AuthService
    from app.schemas.user import UserCreate
    
    # Check if user already exists
    user_service = UserService(db)
    existing_user = user_service.get_user_by_email(email)
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "User with this email already exists"
        })
    
    # Create new user
    user_create = UserCreate(
        email=email,
        username=username,
        password=password,
        full_name=full_name
    )
    
    try:
        user = user_service.create_user(user_create)
        return templates.TemplateResponse("register_success.html", {
            "request": request,
            "email": email
        })
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Error creating user"
        })


@router.post("/auth/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """Handle logout"""
    print("Logout endpoint called")
    request.session.clear()
    print("Session cleared, redirecting to /")
    return RedirectResponse(url="/", status_code=303)


@router.get("/activate/{activation_token}", response_class=HTMLResponse)
async def activate_account(
    request: Request,
    activation_token: str,
    db: Session = Depends(get_db)
):
    """Activate user account"""
    user_service = UserService(db)
    user = user_service.activate_user(activation_token)
    
    if user:
        return templates.TemplateResponse("activation_success.html", {
            "request": request,
            "username": user.username
        })
    else:
        return templates.TemplateResponse("activation_error.html", {
            "request": request
        })


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin panel page"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    if not user.get("is_superuser"):
        return templates.TemplateResponse("404.html", {
            "request": request,
            "error_type": "admin_access"
        })
    
    db = next(get_db())
    user_service = UserService(db)
    settings_service = SettingsService(db)
    
    users = user_service.get_users()
    settings = settings_service.get_settings()
    
    stats = {
        "total_users": len(users),
        "active_users": len([u for u in users if u.is_active]),
        "inactive_users": len([u for u in users if not u.is_active]),
        "total_settings": len(settings)
    }
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "stats": stats
    })


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_table(
    request: Request, 
    sort: str = Query(None),
    order: str = Query("asc"),
    user: dict = Depends(require_admin)
):
    """HTMX endpoint for users table"""
    db = next(get_db())
    user_service = UserService(db)
    users = user_service.get_users(sort=sort, order=order)
    
    return templates.TemplateResponse("users_table.html", {
        "request": request,
        "users": users,
        "sort": sort,
        "order": order
    })


@router.get("/admin/users/new", response_class=HTMLResponse)
async def new_user_form(request: Request):
    """New user form"""
    # Check authentication manually
    user = get_current_user(request)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to access this page"
        })
    
    if not user.get("is_superuser"):
        return templates.TemplateResponse("404.html", {
            "request": request,
            "error_type": "admin_access"
        })
    
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user": None
    })


@router.get("/admin/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Edit user form"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        from app.core.exceptions import UserNotFoundException
        raise UserNotFoundException()
    
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user": user
    })


@router.post("/admin/users", response_class=HTMLResponse)
async def create_user_admin(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    is_active: str = Form("false"),
    is_superuser: str = Form("false"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create user from admin panel"""
    user_service = UserService(db)
    
    user_create = UserCreate(
        email=email,
        username=username,
        password=password,
        full_name=full_name,
        is_active=is_active.lower() == "true"
    )
    
    try:
        user = user_service.create_user(user_create)
        # Update superuser status
        if is_superuser.lower() == "true":
            user.is_superuser = True
            db.commit()
        
        # Return updated users table
        users = user_service.get_users()
        return templates.TemplateResponse("users_table.html", {
            "request": request,
            "users": users
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error creating user")


@router.put("/admin/users/{user_id}", response_class=HTMLResponse)
async def update_user_admin(
    request: Request,
    user_id: int,
    email: str = Form(...),
    username: str = Form(...),
    full_name: str = Form(None),
    is_active: str = Form("false"),
    is_superuser: str = Form("false"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user from admin panel"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        from app.core.exceptions import UserNotFoundException
        raise UserNotFoundException()
    
    user_update = UserUpdate(
        email=email,
        username=username,
        full_name=full_name,
        is_active=is_active.lower() == "true"
    )
    
    try:
        updated_user = user_service.update_user(user_id, user_update)
        # Update superuser status
        updated_user.is_superuser = is_superuser.lower() == "true"
        db.commit()
        
        # Return updated users table
        users = user_service.get_users()
        return templates.TemplateResponse("users_table.html", {
            "request": request,
            "users": users
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error updating user")


@router.delete("/admin/users/{user_id}", response_class=HTMLResponse)
async def delete_user_admin(
    request: Request,
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete user from admin panel"""
    user_service = UserService(db)
    
    try:
        success = user_service.delete_user(user_id)
        if not success:
            from app.core.exceptions import UserNotFoundException
            raise UserNotFoundException()
        
        # Return updated users table
        users = user_service.get_users()
        return templates.TemplateResponse("users_table.html", {
            "request": request,
            "users": users
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error deleting user")


# Settings endpoints
@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_table(
    request: Request, 
    sort: str = Query(None),
    order: str = Query("asc"),
    user: dict = Depends(require_admin)
):
    """HTMX endpoint for settings table"""
    db = next(get_db())
    settings_service = SettingsService(db)
    settings = settings_service.get_settings(sort=sort, order=order)
    
    return templates.TemplateResponse("settings_table.html", {
        "request": request,
        "settings": settings,
        "sort": sort,
        "order": order
    })


@router.get("/admin/settings/new", response_class=HTMLResponse)
async def new_setting_form(request: Request):
    """New setting form"""
    # Check authentication manually
    user = get_current_user(request)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Please login to access this page"
        })
    
    if not user.get("is_superuser"):
        return templates.TemplateResponse("404.html", {
            "request": request,
            "error_type": "admin_access"
        })
    
    return templates.TemplateResponse("setting_form.html", {
        "request": request,
        "setting": None
    })


@router.get("/admin/settings/{setting_name}/edit", response_class=HTMLResponse)
async def edit_setting_form(
    request: Request,
    setting_name: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Edit setting form"""
    settings_service = SettingsService(db)
    setting = settings_service.get_setting(setting_name)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return templates.TemplateResponse("setting_form.html", {
        "request": request,
        "setting": setting
    })


@router.post("/admin/settings", response_class=HTMLResponse)
async def create_setting_admin(
    request: Request,
    setting_name: str = Form(...),
    value: str = Form(...),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create setting from admin panel"""
    from app.schemas.settings import SettingsCreate
    settings_service = SettingsService(db)
    
    # Check if setting already exists
    existing_setting = settings_service.get_setting(setting_name)
    if existing_setting:
        raise HTTPException(status_code=400, detail="Setting already exists")
    
    setting_create = SettingsCreate(setting_name=setting_name, value=value)
    
    try:
        settings_service.create_setting(setting_create)
        
        # Return updated settings table
        settings = settings_service.get_settings()
        return templates.TemplateResponse("settings_table.html", {
            "request": request,
            "settings": settings
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error creating setting")


@router.put("/admin/settings/{setting_name}", response_class=HTMLResponse)
async def update_setting_admin(
    request: Request,
    setting_name: str,
    value: str = Form(...),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update setting from admin panel"""
    from app.schemas.settings import SettingsUpdate
    settings_service = SettingsService(db)
    
    setting_update = SettingsUpdate(value=value)
    
    try:
        updated_setting = settings_service.update_setting(setting_name, setting_update)
        if not updated_setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        # Return updated settings table
        settings = settings_service.get_settings()
        return templates.TemplateResponse("settings_table.html", {
            "request": request,
            "settings": settings
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error updating setting")


@router.delete("/admin/settings/{setting_name}", response_class=HTMLResponse)
async def delete_setting_admin(
    request: Request,
    setting_name: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete setting from admin panel"""
    settings_service = SettingsService(db)
    
    try:
        success = settings_service.delete_setting(setting_name)
        if not success:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        # Return updated settings table
        settings = settings_service.get_settings()
        return templates.TemplateResponse("settings_table.html", {
            "request": request,
            "settings": settings
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error deleting setting")
