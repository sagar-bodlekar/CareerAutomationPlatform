.PHONY: help install dev-up dev-down test lint migrate seed clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -e backend/shared/
	pip install -r backend/requirements-shared.txt

dev-up: ## Start all infrastructure services
	docker compose up -d postgres redis minio

dev-down: ## Stop all infrastructure services
	docker compose down

test: ## Run all tests
	pytest backend/ -v --tb=short

lint: ## Run linters
	ruff check backend/
	black --check backend/

format: ## Format code
	black backend/
	ruff --fix backend/

typecheck: ## Run mypy type checking
	mypy backend/ --strict || true

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migrate-new: ## Create a new migration
	cd backend && alembic revision --autogenerate -m "$(message)"

migrate-rollback: ## Rollback last migration
	cd backend && alembic downgrade -1

seed: ## Seed database with sample data
	python scripts/seed_data.py

clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
