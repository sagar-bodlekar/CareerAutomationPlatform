#!/bin/bash
# Database Migration Runner
# Usage: bash backend/scripts/migrate.sh [upgrade|downgrade|revision|reset]
#   upgrade   - Run all pending migrations (default)
#   downgrade - Rollback last migration
#   revision  - Create a new auto-generated migration
#   reset     - Drop all tables and re-run all migrations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MIGRATE_CMD="cd $BACKEND_DIR && alembic"

ACTION="${1:-upgrade}"
MESSAGE="${2:-auto_migration}"

case "$ACTION" in
    upgrade)
        echo "Running all pending migrations..."
        eval "$MIGRATE_CMD upgrade head"
        echo "✅ Migrations up to date."
        ;;

    downgrade)
        echo "Rolling back last migration..."
        eval "$MIGRATE_CMD downgrade -1"
        echo "✅ Rolled back one migration."
        ;;

    revision)
        echo "Creating new migration: $MESSAGE..."
        eval "$MIGRATE_CMD revision --autogenerate -m \"$MESSAGE\""
        echo "✅ Migration created."
        ;;

    reset)
        echo "⚠️  WARNING: This will DROP ALL TABLES and re-run all migrations!"
        read -p "Are you sure? (y/N): " CONFIRM
        if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
            echo "Dropping all tables..."
            eval "$MIGRATE_CMD downgrade base"
            echo "Running all migrations..."
            eval "$MIGRATE_CMD upgrade head"
            echo "✅ Database reset complete."
        else
            echo "Cancelled."
        fi
        ;;

    *)
        echo "Usage: bash $0 [upgrade|downgrade|revision|reset] [message]"
        exit 1
        ;;
esac
