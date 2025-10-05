
.PHONY: help check-env check-test-env check-prod-safe build build-prod up down dev dev-stop prod prod-up prod-down prod-clean prod-migrate clean prune logs logs-once logs-backend logs-db logs-redis db-shell db-list shell health migrate migrate-test migrate-prod revision check-migrations test test-unit test-integration test-quick test-common test-graphql test-editor test-coverage ci-test lint format fix-lint uv-setup uv-install uv-sync uv-lock uv-add uv-remove uv-run

ENVIRONMENT ?= development

ifneq ($(wildcard .env.local),)
include .env.local
export
endif

ifeq ($(ENVIRONMENT),test)
POSTGRES_DB ?= helpcenter_testdb
else
POSTGRES_DB ?= helpcenter_devdb
endif

ifeq ($(ENVIRONMENT),test)
TEST_DATABASE_URL_ASYNC ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)
else
TEST_DATABASE_URL_ASYNC ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/helpcenter_testdb
endif


check-env:
	@if [ -z "$$DATABASE_URL_ASYNC" ]; then \
		echo "ERROR: DATABASE_URL_ASYNC is not set. Set it in .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@if [ -z "$$POSTGRES_USER" ]; then \
		echo "ERROR: POSTGRES_USER is not set. Set it in .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@if [ -z "$$POSTGRES_PASSWORD" ]; then \
		echo "ERROR: POSTGRES_PASSWORD is not set. Set it in .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@if [ -z "$$POSTGRES_DB" ]; then \
		echo "ERROR: POSTGRES_DB is not set. Set it in .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@echo "Environment variables validated"

check-test-env:
	@if [ -z "$$TEST_DATABASE_URL_ASYNC" ]; then \
		echo "ERROR: TEST_DATABASE_URL_ASYNC is not set. Set it in .env.local or CI/CD secrets."; \
		exit 1; \
	fi
	@echo "Test environment variables validated"

check-prod-safe:
	@if [ "$(ENVIRONMENT)" = "production" ]; then \
		echo "ERROR: This target is not allowed in production environment."; \
		echo "Use 'make prod-up' or 'make prod-migrate' for production operations."; \
		exit 1; \
	fi


.PHONY: help check-env check-test-env check-prod-safe migrate revision migrate-test migrate-prod build build-prod \
        up down clean prune test test-quick test-common test-graphql test-editor test-integration test-coverage ci-test \
        logs logs-backend logs-db logs-redis logs-once shell editor \
        db-shell db-list check-migrations dev dev-stop health lint format \
        uv-setup uv-install uv-run uv-add uv-remove uv-lock uv-sync


help: ## Show this help
	@echo "$(GREEN)Usage: make [target] [ENVIRONMENT=development|test|production]$(RESET)"
	@echo ""
	@echo "Environment-specific targets:"
	@echo "  make dev          - Start development environment"
	@echo "  make test         - Run tests (uses test database)"
	@echo "  make test-quick   - Run tests without cleanup"
	@echo "  make test-common  - Run common package tests only"
	@echo "  make test-graphql - Run GraphQL API tests only"
	@echo "  make test-editor  - Run Editor API tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make prod-up      - Start production environment"
	@echo ""
	@echo "uv dependency management:"
	@echo "  make uv-setup     - Initial uv setup"
	@echo "  make uv-install   - Install dependencies with uv"
	@echo "  make uv-run       - Run GraphQL API with uv"
	@echo "  make uv-add       - Add new dependency (usage: make uv-add pkg=requests)"
	@echo "  make uv-remove    - Remove dependency (usage: make uv-remove pkg=requests)"
	@echo "  make uv-lock      - Update lock file"
	@echo "  make uv-sync      - Sync dependencies"
	@echo ""
	@echo "Environment variables (set via .env.local for dev, CI secrets for prod):"
	@echo "  DATABASE_URL_ASYNC, TEST_DATABASE_URL_ASYNC, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB"
	@echo "  REDIS_URL, SECRET_KEY, DEV_EDITOR_KEY, GCS_BUCKET_NAME, HELPCENTER_GCS, ALLOWED_ORIGINS"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)


migrate: check-env ## Run database migrations
	docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=$(ENVIRONMENT) backend python3 scripts/migrate.py --env $(ENVIRONMENT) --database-url $(DATABASE_URL_ASYNC)

revision: check-prod-safe ## Create a new migration (NOT ALLOWED IN PRODUCTION)
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-test: check-test-env ## Run migrations on test DB (TEST-ONLY TARGET)
	docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=test -e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) backend uv run python -m alembic upgrade head

migrate-prod: check-env ## Run migrations on production DB
	docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=production backend python3 scripts/migrate.py --env production --database-url $(DATABASE_URL_ASYNC)

check-migrations: ## Check migration status
	docker compose run --rm -e PYTHONPATH=/code backend python3 scripts/migrate.py --check


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


ci-test: check-test-env check-prod-safe ## CI mode: reset, abort on exit, propagate exit code (TEST-ONLY TARGET)
	$(MAKE) clean
	docker compose up -d db redis
	$(MAKE) migrate-test
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; uv run python -m pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'
	$(MAKE) clean



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

db-shell: check-prod-safe ## Open database shell (NOT ALLOWED IN PRODUCTION)
	docker compose exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-list: check-prod-safe ## List databases (NOT ALLOWED IN PRODUCTION)
	docker compose exec db psql -U $(POSTGRES_USER) -c "\l"


prod-up: ## Start production services (requires env vars to be set)
	@echo "Starting production services..."
	@echo "Make sure to set: DATABASE_URL_ASYNC, REDIS_URL, SECRET_KEY, DEV_EDITOR_KEY, GCS_BUCKET_NAME, HELPCENTER_GCS, ALLOWED_ORIGINS"
	ENVIRONMENT=production docker compose up -d db redis && sleep 10
	ENVIRONMENT=production docker compose up backend

prod-down: ## Stop production services
	ENVIRONMENT=production docker compose down

prod-clean: ## Clean production resources
	ENVIRONMENT=production docker compose down -v --remove-orphans

prod-migrate: ## Run production migrations (requires DATABASE_URL_ASYNC to be set)
	@echo "Running production migrations..."
	@echo "Make sure to set: DATABASE_URL_ASYNC"
	ENVIRONMENT=production docker compose run --rm -e PYTHONPATH=/code backend python3 scripts/migrate.py --env production --database-url $(DATABASE_URL_ASYNC)


dev: ## Start development environment
	$(MAKE) up ENVIRONMENT=development

test: test-unit test-integration ## Run all tests (unit + integration)

test-unit: ## Run unit tests (fast, no database)
	@echo "Running unit tests (no database required)..."
	docker compose run --rm --no-deps \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; uv run python -m pytest tests/unit/ -c /code/pytest.ini -q --disable-warnings -v'

test-integration: check-test-env check-prod-safe ## Run integration tests (with database)
	@echo "Running integration tests (database required)..."
	$(MAKE) clean
	docker compose up -d db redis
	sleep 5
	$(MAKE) migrate-test
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		-e SECRET_KEY=$(SECRET_KEY) \
		-e DEV_EDITOR_KEY=$(DEV_EDITOR_KEY) \
		-e REDIS_URL=$(REDIS_URL) \
		-e ALLOWED_ORIGINS=$(ALLOWED_ORIGINS) \
		-e GCS_BUCKET_NAME=$(GCS_BUCKET_NAME) \
		-e HELPCENTER_GCS=$(HELPCENTER_GCS) \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; uv run python -m pytest tests/integration/ -c /code/pytest.ini -q --disable-warnings -v'
	$(MAKE) clean

test-quick: check-test-env check-prod-safe ## Run tests without cleanup (faster for development) (TEST-ONLY TARGET)
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; uv run python -m pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'

prod: ## Start production environment
	$(MAKE) up ENVIRONMENT=production


dev-stop: check-prod-safe ## Stop development environment (NOT ALLOWED IN PRODUCTION)
	docker compose down


health: ## Check API health
	curl -s http://localhost:8000/health | jq

lint: check-prod-safe ## Run code linting (NOT ALLOWED IN PRODUCTION)
	docker compose run --rm backend bash -c 'cd /code && uv sync --group dev && uv run python -m flake8 common/ graphql_api/ editor_api/ --max-line-length=100 --ignore=E203,W503,F821,E402'

format: check-prod-safe ## Format code with black (NOT ALLOWED IN PRODUCTION)
	docker compose run --rm backend bash -c 'cd /code && uv sync --group dev && uv run python -m black common/ graphql_api/ editor_api/ --line-length=100'

fix-lint: check-prod-safe ## Fix linting issues automatically (NOT ALLOWED IN PRODUCTION)
	docker compose run --rm backend bash -c 'cd /code && uv sync --group dev && uv run python -m autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables common/ graphql_api/ editor_api/'
	docker compose run --rm backend bash -c 'cd /code && uv run python -m isort common/ graphql_api/ editor_api/ --profile black'
	docker compose run --rm backend bash -c 'cd /code && uv run python -m black common/ graphql_api/ editor_api/ --line-length=100'


uv-setup: ## Initial uv setup and installation
	@echo "Setting up uv..."
	@chmod +x scripts/setup-uv.sh
	@./scripts/setup-uv.sh

uv-install: ## Install dependencies with uv
	@echo "Installing dependencies with uv..."
	uv sync

uv-run: ## Run GraphQL API with uv
	@echo "Running GraphQL API with uv..."
	uv run uvicorn graphql-api.main:app --host 0.0.0.0 --port 8000 --reload

uv-add: ## Add new dependency (usage: make uv-add pkg=requests)
	@if [ -z "$(pkg)" ]; then \
		echo "ERROR: Please specify package name. Usage: make uv-add pkg=requests"; \
		exit 1; \
	fi
	@echo "Adding dependency: $(pkg)"
	uv add $(pkg)

uv-remove: ## Remove dependency (usage: make uv-remove pkg=requests)
	@if [ -z "$(pkg)" ]; then \
		echo "ERROR: Please specify package name. Usage: make uv-remove pkg=requests"; \
		exit 1; \
	fi
	@echo "Removing dependency: $(pkg)"
	uv remove $(pkg)

uv-lock: ## Update lock file
	@echo "Updating lock file..."
	uv lock

uv-sync: ## Sync dependencies
	@echo "Syncing dependencies..."
	uv sync

test-common: ## Run common package unit tests only
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		backend bash -lc 'cd /code && uv run python -m pytest tests/unit/ -c /code/pytest.ini -q --disable-warnings -v'

test-graphql: ## Run GraphQL API integration tests only
	$(MAKE) clean
	docker compose up -d db redis
	sleep 5
	$(MAKE) migrate-test
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && uv run python -m pytest tests/integration/graphql_api/ -c /code/pytest.ini -q --disable-warnings -v'
	$(MAKE) clean

test-editor: ## Run Editor API integration tests only
	$(MAKE) clean
	docker compose up -d db redis
	sleep 5
	$(MAKE) migrate-test
	docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e TEST_DATABASE_URL_ASYNC=$(TEST_DATABASE_URL_ASYNC) \
		backend bash -lc 'cd /code && uv run python -m pytest tests/integration/editor_api/ -c /code/pytest.ini -q --disable-warnings -v'
	$(MAKE) clean

test-coverage: ## Run tests with coverage report
	uv run pytest --cov=common --cov=graphql_api --cov=editor_api --cov-report=html --cov-report=term-missing
