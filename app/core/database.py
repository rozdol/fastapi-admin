from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLite Engine (for users and settings)
sqlite_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# PostgreSQL Database 1 Engine
postgres_db1_engine = create_engine(
    settings.POSTGRES_DB1_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# PostgreSQL Database 2 Engine
postgres_db2_engine = create_engine(
    settings.POSTGRES_DB2_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Session Factories
SQLiteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
PostgresDB1SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_db1_engine)
PostgresDB2SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_db2_engine)

# Base classes for different databases
SQLiteBase = declarative_base()
PostgresDB1Base = declarative_base()
PostgresDB2Base = declarative_base()


def get_sqlite_db():
    """Dependency for SQLite database sessions (users and settings)"""
    db = SQLiteSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_postgres_db1():
    """Dependency for PostgreSQL Database 1 sessions"""
    db = PostgresDB1SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_postgres_db2():
    """Dependency for PostgreSQL Database 2 sessions"""
    db = PostgresDB2SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Legacy support - maps to SQLite database
def get_db():
    """Legacy database dependency - maps to SQLite database"""
    return get_sqlite_db()


# Import all models to ensure they are registered with SQLAlchemy
# This is handled by the models __init__.py file
