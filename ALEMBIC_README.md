# Alembic Database Migrations Guide

This project uses Alembic for database migrations with FastAPI, Docker, and PostgreSQL.

## 🚀 Quick Start

### Prerequisites
- Database running (Docker or local)
- Virtual environment activated
- Environment variables set (DATABASE_URL)

### Initial Setup

1. **Create your first migration:**
   ```bash
   source venv/bin/activate
   alembic revision --autogenerate -m "Initial migration"
   ```

2. **Apply migrations:**
   ```bash
   alembic upgrade head
   ```

## 📋 Common Commands

### Using Helper Script (Recommended)
```bash
# Make script executable
chmod +x run_migrations.sh

# Create new migration
./run_migrations.sh revision "Add new table"

# Apply migrations
./run_migrations.sh upgrade

# Show migration history
./run_migrations.sh history

# Show current revision
./run_migrations.sh current
```

### Using Alembic Directly
```bash
source venv/bin/activate

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Apply one migration
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show migration history
alembic history

# Show current database revision
alembic current
```

## 🐳 Docker Usage

### Option 1: Run migrations inside Docker container
```bash
# Start containers
docker-compose up -d db

# Run migrations in container
docker-compose exec api alembic upgrade head
```

### Option 2: Run migrations locally (Hybrid approach)
```bash
# Start only database
docker-compose up -d db

# Set database URL
export DATABASE_URL="postgresql+psycopg2://postgres:postgres123@localhost:5433/fastapi_app"

# Run migrations locally
source venv/bin/activate
alembic upgrade head
```

## 📝 Creating Migrations

### Auto-generate from Models
```bash
# After modifying models in app/models/
alembic revision --autogenerate -m "Add new field to User model"
```

### Manual Migration
```bash
# Create empty migration file
alembic revision -m "Custom migration"
# Then edit the generated file in alembic/versions/
```

## 🔍 Important Notes

1. **Always import your models in `alembic/env.py`** - This ensures Alembic can detect model changes
   ```python
   from app.models.user import User
   ```

2. **Review auto-generated migrations** - Always check the generated migration file before applying it

3. **Database URL** - Make sure `DATABASE_URL` environment variable is set correctly:
   - Docker: `postgresql+psycopg2://postgres:postgres123@db:5432/fastapi_app`
   - Local: `postgresql+psycopg2://postgres:postgres123@localhost:5433/fastapi_app`

## 🛠️ Troubleshooting

### Migration conflicts
```bash
# Check current state
alembic current

# Show history
alembic history

# Resolve conflicts manually if needed
```

### Database connection errors
- Ensure database is running: `docker-compose ps`
- Check DATABASE_URL is correct
- Verify network connectivity

### Models not detected
- Ensure models are imported in `alembic/env.py`
- Check that models inherit from `Base`
- Verify `target_metadata = Base.metadata` in `env.py`

## 📚 Best Practices

1. **Always create migrations for schema changes**
2. **Test migrations on development database first**
3. **Keep migration files in version control**
4. **Use descriptive migration messages**
5. **Review auto-generated migrations before applying**
6. **Backup database before major migrations**

## 🔗 Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
