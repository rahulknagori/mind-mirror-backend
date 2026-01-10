#!/bin/bash

# Alembic Migration Helper Script
# Usage: ./run_migrations.sh [command]
# Commands: upgrade, downgrade, revision, history, current

# Set environment variables
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://postgres:postgres123@localhost:5433/fastapi_app}"

# Activate virtual environment
source venv/bin/activate

# Run alembic command
if [ -z "$1" ]; then
    echo "Usage: ./run_migrations.sh [command]"
    echo ""
    echo "Commands:"
    echo "  upgrade [revision]  - Upgrade to a specific revision (default: head)"
    echo "  downgrade [revision] - Downgrade to a specific revision"
    echo "  revision [message]  - Create a new migration"
    echo "  history            - Show migration history"
    echo "  current             - Show current revision"
    echo "  autogenerate        - Create migration from models (auto)"
    exit 1
fi

case "$1" in
    upgrade)
        alembic upgrade "${2:-head}"
        ;;
    downgrade)
        alembic downgrade "${2:--1}"
        ;;
    revision)
        alembic revision --autogenerate -m "${2:-Auto migration}"
        ;;
    history)
        alembic history
        ;;
    current)
        alembic current
        ;;
    autogenerate)
        alembic revision --autogenerate -m "${2:-Auto migration}"
        ;;
    *)
        echo "Unknown command: $1"
        exit 1
        ;;
esac
