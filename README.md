# FastAPI Application

A modern FastAPI application with a well-structured architecture for medium-sized projects.

## Features

- FastAPI with automatic API documentation
- SQLAlchemy ORM with Alembic migrations
- JWT authentication
- Pydantic data validation
- **Modern HTMX Frontend** with Tailwind CSS
- **Admin Panel** with user management
- **Session-based authentication** for web interface
- Comprehensive testing setup
- Code formatting and linting
- Modular architecture

## Project Structure

```
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   └── users.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── user.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── user_service.py
│   ├── utils/
│   │   └── helpers.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_users.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── requirements.txt
├── alembic.ini
└── README.md
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./app.db
   ENVIRONMENT=development
   DEBUG=true
   ```

3. **Initialize database:**
   ```bash
   alembic upgrade head
   ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, you can access:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## Frontend Interface

The application includes a modern web interface:
- **Home Page:** http://localhost:8000/
- **Login:** http://localhost:8000/login
- **Register:** http://localhost:8000/register
- **Admin Panel:** http://localhost:8000/admin (requires admin login)
- **Custom 404 Pages:** Beautiful error pages for access denied and missing pages

### Test Users
- **Admin:** test@example.com / testpassword
- **Regular User:** newuser@example.com / newpassword

## Available Endpoints

### API Endpoints
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{user_id}` - Get specific user
- `POST /api/v1/users/` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/auth/login` - JWT login
- `POST /api/v1/auth/register` - JWT registration

### Frontend Pages
- `GET /` - Home page
- `GET /login` - Login page
- `GET /register` - Registration page
- `GET /admin` - Admin panel (requires admin authentication)
- `POST /auth/login` - Web login form
- `POST /auth/register` - Web registration form
- `POST /auth/logout` - Logout
- Custom 404 pages for admin access denied and general errors

## Testing

Run tests with:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

## Code Quality

Format code:
```bash
black app/
isort app/
```

Lint code:
```bash
flake8 app/
mypy app/
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Development

The application follows a clean architecture pattern:
- **Models:** SQLAlchemy database models
- **Schemas:** Pydantic models for data validation
- **Services:** Business logic layer
- **API:** FastAPI route handlers
- **Core:** Configuration and utilities
