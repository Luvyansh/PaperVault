#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting Backend Initialization Sequence..."

echo "1/2: Running initial schema setup..."
python init_db.py

echo "2/2: Applying Alembic migrations (including Power BI views)..."
alembic upgrade head

echo "✅ Backend Database is fully configured and ready!"