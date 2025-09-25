# ---------------------------
# Environment setup
# ---------------------------

# Default environment
ENVIRONMENT ?= development

# Load .env.local if it exists
ifneq ($(wildcard .env.local),)
include .env.local
export
endif

# Environment-specific database configuration
ifeq ($(ENVIRONMENT),test)
POSTGRES_DB ?= helpcenter_testdb
else
POSTGRES_DB ?= helpcenter_devdb
endif

# Set test database URL based on environment
ifeq ($(ENVIRONMENT),test)
TEST_DATABASE_URL_ASYNC ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)
else
TEST_DATABASE_URL_ASYNC ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/helpcenter_testdb
endif

# ---------------------------
# Environment validation
# ---------------------------

# Check for required environment variables
check-env:
	@if [ -z "$$DATABASE_URL_ASYNC" ]; then \
		echo "ERROR: DATABASE_URL_ASYNC is not set. Please set it in your .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@if [ -z "$$POSTGRES_USER" ]; then \
		echo "ERROR: POSTGRES_USER is not set. Please set it in your .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@if [ -z "$$POSTGRES_PASSWORD" ]; then \
		echo "ERROR: POSTGRES_PASSWORD is not set. Please set it in your .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@if [ -z "$$POSTGRES_DB" ]; then \
		echo "ERROR: POSTGRES_DB is not set. Please set it in your .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@echo "Environment variables validated"

# Check for test environment variables
check-test-env:
	@if [ -z "$$TEST_DATABASE_URL_ASYNC" ]; then \
		echo "ERROR: TEST_DATABASE_URL_ASYNC is not set. Please set it in your .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@echo "Test environment variables validated"

# Check if target is allowed in production
check-prod-safe:
	@if [ "$(ENVIRONMENT)" = "production" ]; then \
		echo "ERROR: This target is not allowed in production environment."; \
		echo "Use 'make prod-up' or 'make prod-migrate' for production operations."; \
		exit 1; \
	fi

# ---------------------------
# Phony targets
# ---------------------------

.PHONY: help check-env check-test-env check-prod-safe migrate revision migrate-test migrate-prod build build-prod \
        up down clean prune test test-quick ci-test \
        logs logs-backend logs-db logs-redis logs-once shell editor \
        db-shell db-list check-migrations dev dev-stop health lint format

# ---------------------------
# Help
# ---------------------------

help: ## Show this help
	@echo "Usage: make [target] [ENVIRONMENT=development|test|production]"
	@echo ""
	@echo "Environment-specific targets:"
	@echo "  make dev          - Start development environment"
	@echo "  make test         - Run tests (uses test database)"
	@echo "  make test-quick   - Run tests without cleanup"
	@echo "  make prod-up      - Start production environment"
	@echo ""
	@echo "Environment variables (set via .env.local for dev, CI secrets for prod):"
	@echo "  DATABASE_URL_ASYNC, TEST_DATABASE_URL_ASYNC, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB"
	@echo "  REDIS_URL, SECRET_KEY, DEV_EDITOR_KEY, GCS_BUCKET_NAME, HELPCENTER_GCS, ALLOWED_ORIGINS"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ---------------------------
# Database & migrations
# ---------------------------

migrate: check-env ## Run database migrations
	docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=$(ENVIRONMENT) backend python3 scripts/migrate.py --env $(ENVIRONMENT) --database-url $(DATABASE_URL_ASYNC)

revision: check-prod-safe ## Create a new migration (NOT ALLOWED IN PRODUCTION)
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-test: check-test-env ## Run migrations on test DB (TEST-ONLY TARGET)
	docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=test -e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) backend python3 scripts/migrate.py --env test --database-url $(TEST_DATABASE_URL_ASYNC)

migrate-prod: check-env ## Run migrations on production DB
	docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=production backend python3 scripts/migrate.py --env production --database-url $(DATABASE_URL_ASYNC)

check-migrations: ## Check migration status
	docker compose run --rm -e PYTHONPATH=/code backend python3 scripts/migrate.py --check

# ---------------------------
# Build & services
# ---------------------------

build: check-prod-safe ## Build Docker images (NOT ALLOWED IN PRODUCTION)
	docker compose build

build-prod: ## Build production Docker image
	docker build -f Dockerfile.prod -t helpcenter-backend:latest .

up: check-env ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

clean: check-prod-safe ## Stop services and remove volumes (NOT ALLOWED IN PRODUCTION)
	docker compose down -v --remove-orphans

prune: check-prod-safe ## Remove all Docker resources (NOT ALLOWED IN PRODUCTION)
	docker system prune -af

# ---------------------------
# Tests
# ---------------------------

ci-test: check-test-env check-prod-safe ## CI mode: reset, abort on exit, propagate exit code (TEST-ONLY TARGET)
	$(MAKE) clean
	docker compose up -d db redis
	$(MAKE) migrate-test
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'
	$(MAKE) clean


# ---------------------------
# Logs & shells
# ---------------------------

logs: check-prod-safe ## Show logs for all services (NOT ALLOWED IN PRODUCTION)
	docker compose logs -f

logs-backend: check-prod-safe ## Show backend logs (NOT ALLOWED IN PRODUCTION)
	docker compose logs -f backend

logs-db: check-prod-safe ## Show database logs (NOT ALLOWED IN PRODUCTION)
	docker compose logs -f db

logs-redis: check-prod-safe ## Show Redis logs (NOT ALLOWED IN PRODUCTION)
	docker compose logs -f redis

logs-once: check-prod-safe ## Show logs once (NOT ALLOWED IN PRODUCTION)
	docker compose logs

shell: check-prod-safe ## Open shell in backend container (NOT ALLOWED IN PRODUCTION)
	docker compose run --rm backend bash

editor: check-prod-safe ## Run the help center editor (NOT ALLOWED IN PRODUCTION)
	python scripts/demo/editor.py

db-shell: check-prod-safe ## Open database shell (NOT ALLOWED IN PRODUCTION)
	docker compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-list: check-prod-safe ## List databases (NOT ALLOWED IN PRODUCTION)
	docker compose exec db psql -U $(POSTGRES_USER) -c "\l"

# ---------------------------
# Production shortcuts
# ---------------------------

prod-up: ## Start production services (requires env vars to be set)
	@echo "Starting production services..."
	@echo "Make sure to set: DATABASE_URL_ASYNC, REDIS_URL, SECRET_KEY, DEV_EDITOR_KEY, GCS_BUCKET_NAME, HELPCENTER_GCS, ALLOWED_ORIGINS"
	ENVIRONMENT=production docker compose up -d db redis
	sleep 5
	ENVIRONMENT=production docker compose up backend

prod-down: ## Stop production services
	ENVIRONMENT=production docker compose down

prod-clean: ## Clean production resources
	ENVIRONMENT=production docker compose down -v --remove-orphans

prod-migrate: ## Run production migrations (requires DATABASE_URL_ASYNC to be set)
	@echo "Running production migrations..."
	@echo "Make sure to set: DATABASE_URL_ASYNC"
	ENVIRONMENT=production docker compose run --rm -e PYTHONPATH=/code backend python3 scripts/migrate.py --env production --database-url $(DATABASE_URL_ASYNC)

# ---------------------------
# Environment-specific targets
# ---------------------------

dev: ## Start development environment
	$(MAKE) up ENVIRONMENT=development

test: check-test-env check-prod-safe ## Run full test suite with cleanup (TEST-ONLY TARGET)
	$(MAKE) clean
	docker compose up -d db redis
	sleep 5
	$(MAKE) migrate-test
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'
	$(MAKE) clean

test-quick: check-test-env check-prod-safe ## Run tests without cleanup (faster for development) (TEST-ONLY TARGET)
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'

prod: ## Start production environment
	$(MAKE) up ENVIRONMENT=production

# ---------------------------
# Dev shortcuts
# ---------------------------

dev-stop: check-prod-safe ## Stop development environment (NOT ALLOWED IN PRODUCTION)
	docker compose down

# ---------------------------
# Utilities
# ---------------------------

health: ## Check API health
	curl -s http://localhost:8000/health | jq

lint: check-prod-safe ## Run code linting (NOT ALLOWED IN PRODUCTION)
	docker compose run --rm backend bash -c 'cd /code && python -m flake8 app/ --max-line-length=100 --ignore=E203,W503,F821,E402'

format: check-prod-safe ## Format code with black (NOT ALLOWED IN PRODUCTION)
	docker compose run --rm backend bash -c 'cd /code && python -m black app/ --line-length=100'