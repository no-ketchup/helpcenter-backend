ifneq ($(CI),true)
ifneq ($(wildcard .env.local),)
include .env.local
export
endif
endif

ENV_FILE ?= .env.local
COMPOSE = docker compose --env-file $(ENV_FILE)

.PHONY: help migrate revision migrate-test build up down clean prune test ci-test \
        logs logs-backend logs-db logs-redis logs-once shell db-shell db-list \
        prod-up prod-down prod-clean prod-migrate check-migrations \
        dev dev-stop health editor test-quick lint format

help: ## Show this help
	@echo "Usage: make [target] [ENV_FILE=.env.local or .env.prod]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

migrate: ## Run database migrations
	python3 scripts/migrate.py --env development

revision: ## Create a new migration
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-test: ## Run migrations on test DB
	python3 scripts/migrate.py --env test --database-url $(TEST_DATABASE_URL_ASYNC)

migrate-prod: ## Run migrations on production DB
	python3 scripts/migrate.py --env production --database-url $(DATABASE_URL_ASYNC)

build: ## Build Docker images
	$(COMPOSE) build

build-prod: ## Build production Docker image
	docker build -f Dockerfile.prod -t helpcenter-backend:latest .

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

clean: ## Stop services and remove volumes
	$(COMPOSE) down -v --remove-orphans

prune: ## Remove all Docker resources
	docker system prune -af

test: ## Run full test suite with cleanup
	$(MAKE) clean ENV_FILE=.env.local
	$(COMPOSE) up -d db redis
	sleep 5  # Wait for services to be ready
	$(COMPOSE) run --rm -e PYTHONPATH=/code -e ENVIRONMENT=test backend python3 scripts/migrate.py --env test --database-url $(TEST_DATABASE_URL_ASYNC)
	$(COMPOSE) run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'
	$(MAKE) clean ENV_FILE=.env.local

test-quick: ## Run tests without cleanup (faster for development)
	$(COMPOSE) run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'

ci-test: ## CI mode: reset, abort on exit, propagate exit code
	$(MAKE) clean ENV_FILE=.env.local
	$(COMPOSE) up -d db redis
	$(COMPOSE) run --rm -e PYTHONPATH=/code -e ENVIRONMENT=test backend python3 scripts/migrate.py --env test --database-url $(TEST_DATABASE_URL_ASYNC)
	$(COMPOSE) run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'
	$(MAKE) clean ENV_FILE=.env.local

ci-test-no-env: ## CI mode without env file dependency
	ENV_FILE=/dev/null docker compose up -d db redis
	sleep 5
	ENV_FILE=/dev/null docker compose run --rm -e PYTHONPATH=/code -e ENVIRONMENT=test backend python3 scripts/migrate.py --env test --database-url postgresql+asyncpg://postgres:postgres@db:5432/test_db
	ENV_FILE=/dev/null docker compose run --rm \
		-e PYTHONPATH=/code \
		-e ENVIRONMENT=test \
		-e PYTHONDONTWRITEBYTECODE=1 \
		backend bash -lc 'cd /code && find /code -name __pycache__ -type d -prune -exec rm -rf {} +; pytest -c /code/pytest.ini -q --disable-warnings --maxfail=1 -v'
	ENV_FILE=/dev/null docker compose down -v

logs: ## Show logs for all services
	$(COMPOSE) logs -f

logs-backend: ## Show backend logs
	$(COMPOSE) logs -f backend

logs-db: ## Show database logs
	$(COMPOSE) logs -f db

logs-redis: ## Show Redis logs
	$(COMPOSE) logs -f redis

logs-once: ## Show logs once
	$(COMPOSE) logs

shell: ## Open shell in backend container
	$(COMPOSE) run --rm backend bash

editor: ## Run the help center editor
	python scripts/demo/editor.py

db-shell: ## Open database shell
	$(COMPOSE) exec db psql -U helpcenter_devuser -d helpcenter_devdb

db-list: ## List databases
	$(COMPOSE) exec db psql -U helpcenter_devuser -c "\l"

prod-up: ## Start production services
	$(MAKE) up ENV_FILE=.env.prod

prod-down: ## Stop production services
	$(MAKE) down ENV_FILE=.env.prod

prod-clean: ## Clean production resources
	$(MAKE) clean ENV_FILE=.env.prod

prod-migrate: ## Run production migrations
	$(MAKE) migrate ENV_FILE=.env.prod

check-migrations: ## Check migration status
	python3 scripts/migrate.py --check

dev: ## Start development environment (backend + db + redis)
	$(COMPOSE) up -d db redis
	sleep 3
	$(COMPOSE) run --rm -e PYTHONPATH=/code backend python3 scripts/migrate.py --env development
	$(COMPOSE) up backend

dev-stop: ## Stop development environment
	$(COMPOSE) down

health: ## Check API health
	curl -s http://localhost:8000/health | jq

lint: ## Run code linting
	$(COMPOSE) run --rm backend bash -c 'cd /code && python -m flake8 app/ --max-line-length=100 --ignore=E203,W503,F821,E402'

format: ## Format code with black
	$(COMPOSE) run --rm backend bash -c 'cd /code && python -m black app/ --line-length=100'