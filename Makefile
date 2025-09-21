# Default environment file
ENV_FILE ?= .env

# Base docker-compose command
COMPOSE = docker compose --env-file $(ENV_FILE)

# Alembic command (always point to root alembic.ini)
ALEMBIC = $(COMPOSE) run --rm -e PYTHONPATH=/app backend alembic -c alembic.ini

# -------------------------------
# Phony targets
# -------------------------------
.PHONY: help migrate revision build up down test ci-test logs shell prod-up prod-down prod-migrate

# -------------------------------
# Help
# -------------------------------
help: ## Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) \
		| sed -E 's/:.*##/: ##/' \
		| column -t -s '##'

# -------------------------------
# Database & Migrations
# -------------------------------

migrate: ## Run latest migrations
	$(ALEMBIC) upgrade head

revision: ## Create new migration (usage: make revision m="add users table")
	$(ALEMBIC) revision --autogenerate -m "$(m)"

# -------------------------------
# Containers
# -------------------------------

build: ## Build images
	$(COMPOSE) build

up: ## Start stack
	$(COMPOSE) up -d

down: ## Stop stack & clean
	$(COMPOSE) down --volumes --remove-orphans

clean: ## Clean up volumes and images
	docker compose down -v --remove-orphans
	docker system prune -f

# -------------------------------
# Testing
# -------------------------------

test: ## Run tests (reset DB every time)
	$(COMPOSE) down -v --remove-orphans
	$(COMPOSE) up --build -d
	$(MAKE) migrate ENV_FILE=$(ENV_FILE)
	$(COMPOSE) exec -T backend pytest -v
	$(COMPOSE) down -v --remove-orphans

ci-test: ## CI mode: reset, abort on exit, propagate exit code
	ENV_FILE=.env.test $(COMPOSE) down -v --remove-orphans
	ENV_FILE=.env.test $(COMPOSE) up --build --abort-on-container-exit --exit-code-from backend
	ENV_FILE=.env.test $(COMPOSE) down --volumes --remove-orphans

# -------------------------------
# Utilities
# -------------------------------

logs: ## Tail logs
	$(COMPOSE) logs -f

shell: ## Open shell in backend
	$(COMPOSE) exec backend bash

# -------------------------------
# Production (NeonDB)
# -------------------------------

prod-up: ## Start stack with .env.prod
	ENV_FILE=.env.prod $(COMPOSE) up -d

prod-down: ## Stop stack & clean with .env.prod
	ENV_FILE=.env.prod $(COMPOSE) down --volumes --remove-orphans

prod-migrate: ## Run migrations with .env.prod
	ENV_FILE=.env.prod $(ALEMBIC) upgrade head