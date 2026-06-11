#!/bin/bash
# Scaffold a new microservice from the template
# Usage: bash backend/scripts/create_service.sh my_service_name

set -e

if [ $# -lt 1 ]; then
    echo "Usage: bash backend/scripts/create_service.sh <service_name>"
    echo ""
    echo "Example:"
    echo "  bash backend/scripts/create_service.sh profile_service"
    exit 1
fi

SERVICE_NAME=$1
SERVICE_DIR="backend/${SERVICE_NAME}"
TEMPLATE_DIR="backend/service_template"

if [ -d "$SERVICE_DIR" ]; then
    echo "Error: Directory '$SERVICE_DIR' already exists!"
    exit 1
fi

echo "Creating new service: ${SERVICE_NAME}"
echo "Source: ${TEMPLATE_DIR}"
echo "Target: ${SERVICE_DIR}"
echo ""

# Copy template
cp -r "$TEMPLATE_DIR" "$SERVICE_DIR"

# Remove template-specific files
rm -f "$SERVICE_DIR/__init__.py"

# Update service_name in config
sed -i "s/service-template/${SERVICE_NAME}/g" "$SERVICE_DIR/app/core/config.py"
sed -i "s/Service Template/${SERVICE_NAME}/g" "$SERVICE_DIR/app/main.py"
sed -i "s/service_template/${SERVICE_NAME}/g" "$SERVICE_DIR/app/main.py"

# Create migration directory
mkdir -p "$SERVICE_DIR/alembic/versions"
touch "$SERVICE_DIR/alembic/versions/.gitkeep"

echo "✅ Service '${SERVICE_NAME}' created at: ${SERVICE_DIR}"
echo ""
echo "Next steps:"
echo "  1. cd ${SERVICE_DIR}"
echo "  2. Update app/models/models.py with your SQLAlchemy models"
echo "  3. Update app/schemas/ with your Pydantic schemas"
echo "  4. Update app/services/ with your business logic"
echo "  5. Update app/api/v1/endpoints.py with your API endpoints"
echo "  6. Add to docker-compose.yml"
echo ""
