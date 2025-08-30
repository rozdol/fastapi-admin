# Multi-Database Setup Guide

This guide explains how to configure and use three separate databases in your FastAPI application:
- **SQLite**: Users and settings (existing)
- **PostgreSQL Database 1**: Analytics and user logs
- **PostgreSQL Database 2**: System events and performance metrics

## Configuration

### Environment Variables

Create or update your `.env` file with the following database configurations:

```env
# SQLite Database (for users and settings - existing)
DATABASE_URL=sqlite:///./app.db

# PostgreSQL Database 1 (for analytics and user logs)
POSTGRES_DB1_URL=postgresql://username:password@localhost:5432/analytics_db

# PostgreSQL Database 2 (for system events and performance metrics)
POSTGRES_DB2_URL=postgresql://username:password@localhost:5432/monitoring_db
```

### Database Setup

1. **Create PostgreSQL databases:**
```sql
CREATE DATABASE analytics_db;
CREATE DATABASE monitoring_db;
```

or
```bash
createdb -O postgres -E UTF8 -h localhost -p 5432 -U postgres analytics_db
createdb -O postgres -E UTF8 -h localhost -p 5432 -U postgres monitoring_db
```

2. **Create user with permissions:**
```sql
CREATE USER fastapi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE analytics_db TO fastapi_user;
GRANT ALL PRIVILEGES ON DATABASE monitoring_db TO fastapi_user;
```

## Database Organization

### SQLite Database (Primary)
- **Purpose**: Core application data
- **Models**: `User`, `Settings`
- **Dependency**: `get_sqlite_db()` or `get_db()` (legacy)

### PostgreSQL Database 1 (Analytics)
- **Purpose**: User analytics and activity logs
- **Models**: `Analytics`, `UserLog`
- **Dependency**: `get_postgres_db1()`

### PostgreSQL Database 2 (Monitoring)
- **Purpose**: System events and performance metrics
- **Models**: `SystemEvent`, `PerformanceMetric`
- **Dependency**: `get_postgres_db2()`

## Usage

### Database Dependencies

Use the appropriate database dependency in your endpoints:

```python
from app.core.database import get_sqlite_db, get_postgres_db1, get_postgres_db2

# For SQLite database (users, settings)
@router.get("/users")
async def get_users(db: Session = Depends(get_sqlite_db)):
    # Use SQLite database
    pass

# For PostgreSQL Database 1 (analytics)
@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_postgres_db1)):
    # Use PostgreSQL Database 1
    pass

# For PostgreSQL Database 2 (monitoring)
@router.get("/system-events")
async def get_system_events(db: Session = Depends(get_postgres_db2)):
    # Use PostgreSQL Database 2
    pass
```

### Cross-Database Operations

```python
@router.post("/analytics")
async def create_analytics(
    analytics: AnalyticsEventCreate,
    sqlite_db: Session = Depends(get_sqlite_db),
    postgres_db1: Session = Depends(get_postgres_db1)
):
    # First, verify user exists in SQLite database
    user = sqlite_db.query(User).filter(User.id == analytics.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Then create analytics event in PostgreSQL Database 1
    analytics_event = await create_analytics_event(
        user_id=analytics.user_id,
        event_type=analytics.event_type,
        db=postgres_db1
    )
    
    return {"message": "Analytics event created"}
```

### Service Layer Example

```python
from app.core.database import get_postgres_db1

async def create_analytics_event(
    user_id: int,
    event_type: str,
    db: Session = None
) -> Analytics:
    """Create analytics event in PostgreSQL Database 1"""
    if db is None:
        db = next(get_postgres_db1())
    
    analytics = Analytics(
        user_id=user_id,
        event_type=event_type
    )
    
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics
```

## API Endpoints

### PostgreSQL Demo Endpoints

#### Database 1 (Analytics)
- `POST /api/v1/postgres-demo/analytics` - Create analytics event
- `POST /api/v1/postgres-demo/user-log` - Create user log entry
- `GET /api/v1/postgres-demo/analytics` - Get analytics events
- `GET /api/v1/postgres-demo/user-logs` - Get user logs

#### Database 2 (Monitoring)
- `POST /api/v1/postgres-demo/system-event` - Create system event
- `POST /api/v1/postgres-demo/performance-metric` - Create performance metric
- `GET /api/v1/postgres-demo/system-events` - Get system events
- `GET /api/v1/postgres-demo/performance-metrics` - Get performance metrics

### Example Usage

```bash
# Create analytics event (cross-database operation)
curl -X POST "http://localhost:8000/api/v1/postgres-demo/analytics" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "event_type": "page_view",
    "event_data": {"page": "/dashboard", "duration": 30}
  }'

# Create user log entry
curl -X POST "http://localhost:8000/api/v1/postgres-demo/user-log" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "action": "login",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }'

# Create system event
curl -X POST "http://localhost:8000/api/v1/postgres-demo/system-event" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "application_start",
    "severity": "INFO",
    "message": "Application started successfully",
    "event_metadata": {"version": "1.0.0"}
  }'

# Create performance metric
curl -X POST "http://localhost:8000/api/v1/postgres-demo/performance-metric" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "response_time",
    "metric_value": 150.5,
    "unit": "ms",
    "tags": {"endpoint": "/api/users"}
  }'

# Get analytics events
curl "http://localhost:8000/api/v1/postgres-demo/analytics?user_id=1&limit=10"

# Get system events
curl "http://localhost:8000/api/v1/postgres-demo/system-events?severity=ERROR&limit=10"
```

## Model Structure

### SQLite Models (app/models/)
- `user.py` - User accounts and authentication
- `settings.py` - Application settings

### PostgreSQL Database 1 Models (app/models/postgres_db1.py)
- `Analytics` - User analytics events
- `UserLog` - User activity logs

### PostgreSQL Database 2 Models (app/models/postgres_db2.py)
- `SystemEvent` - System events and logs
- `PerformanceMetric` - Performance monitoring data

## Service Layer

### PostgreSQL Database 1 Service (app/services/postgres_db1_service.py)
- `create_analytics_event()` - Create analytics events
- `create_user_log()` - Create user log entries
- `get_user_analytics()` - Retrieve analytics data
- `get_user_logs()` - Retrieve user logs

### PostgreSQL Database 2 Service (app/services/postgres_db2_service.py)
- `create_system_event()` - Create system events
- `create_performance_metric()` - Create performance metrics
- `get_system_events()` - Retrieve system events
- `get_performance_metrics()` - Retrieve performance metrics

## Best Practices

1. **Separation of Concerns**: Keep core data in SQLite, analytics in PostgreSQL DB1, monitoring in PostgreSQL DB2
2. **Connection Pooling**: All databases use connection pooling for better performance
3. **Error Handling**: Always handle database connection errors gracefully
4. **Transactions**: Use transactions when operations span multiple databases
5. **Monitoring**: Monitor all database connections and performance
6. **Data Integrity**: Verify data exists in source database before writing to target database

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if PostgreSQL is running and accessible
2. **Authentication Failed**: Verify username/password in connection strings
3. **Database Not Found**: Ensure databases are created before running the application
4. **Permission Denied**: Check user permissions on both PostgreSQL databases

### Testing Connections

```python
from app.core.database import sqlite_engine, postgres_db1_engine, postgres_db2_engine

# Test SQLite database connection
with sqlite_engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("SQLite DB: OK")

# Test PostgreSQL Database 1 connection
with postgres_db1_engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("PostgreSQL DB1: OK")

# Test PostgreSQL Database 2 connection
with postgres_db2_engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("PostgreSQL DB2: OK")
```

### Migration Strategy

Since you're keeping SQLite for users and settings, no migration is needed for existing data. The PostgreSQL databases will be created fresh with the new models.

## Performance Considerations

1. **Connection Limits**: Monitor connection pool usage for both PostgreSQL databases
2. **Query Optimization**: Use appropriate indexes on PostgreSQL tables
3. **Data Volume**: Consider partitioning for high-volume analytics data
4. **Backup Strategy**: Implement separate backup strategies for each database
