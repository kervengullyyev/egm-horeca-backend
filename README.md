# EGM Horeca Backend

FastAPI backend for the EGM Horeca e-commerce platform.

## Features

- RESTful API with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Alembic database migrations
- JWT authentication
- Stripe payment integration
- File upload handling
- Multi-language support (English & Romanian)

## Database Management

This project uses Alembic for database migrations. The database schema is managed through migration files rather than automatic table creation.

### Prerequisites

- PostgreSQL 12+ running on localhost:5432
- Database `egm_horeca` created
- User `egm_user` with password `egm123`

### Quick Setup

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Initialize database (if tables don't exist):**
   ```bash
   python manage_db.py init
   ```

4. **Seed database with sample data:**
   ```bash
   python manage_db.py seed
   ```

5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Database Commands

Use the `manage_db.py` script for common database operations:

```bash
# Initialize database with migrations
python manage_db.py init

# Run pending migrations
python manage_db.py migrate

# Create new migration
python manage_db.py create "Description of changes"

# Check current version
python manage_db.py current

# Show migration history
python manage_db.py history

# Seed database with sample data
python manage_db.py seed

# Reset database (DANGER: drops all data)
python manage_db.py reset
```

### Manual Alembic Commands

You can also use Alembic directly:

```bash
# Check current version
alembic current

# Show migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Mark current state as specific version
alembic stamp head
```

## API Documentation

Once the server is running, visit:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   ├── env.py           # Alembic environment
│   └── script.py.mako   # Migration template
├── app/                  # Application code
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── api.py           # API endpoints
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application
├── manage_db.py          # Database management script
├── alembic.ini          # Alembic configuration
└── requirements.txt      # Python dependencies
```

## Environment Variables

Key environment variables (see `env.example` for full list):

- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_SECRET_KEY`: Stripe secret key for payments
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
- `FRONTEND_URL`: Frontend URL for CORS
- `ADMIN_URL`: Admin panel URL for CORS
