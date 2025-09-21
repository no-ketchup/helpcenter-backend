# -------------------------------
# Defaults
# -------------------------------
ENV_FILE ?= .env.local
COMPOSE = docker compose --env-file $(ENV_FILE)
ALEMBIC = $(COMPOSE) run --rm -e PYTHONPATH=/app backend alembic -c alembic.ini

# -------------------------------
# Phony targets
# -------------------------------
.PHONY: help migrate revision build up down clean prune test ci-test logs shell \
        prod-up prod-down prod-clean prod-migrate

# -------------------------------
# Help
# -------------------------------
help: ## Show this help
	@echo "Usage: make [target] [ENV_FILE=.env.local or .env.prod]"
	@echo ""
	@echo "Available commands:"
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

down: ## Stop stack (keep volumes)
	$(COMPOSE) down --remove-orphans

clean: ## Stop stack and remove volumes (reset project)
	$(COMPOSE) down -v --remove-orphans

prune: ## Global Docker prune (WARNING: nukes all unused containers, images, cache)
	docker system prune -f

# -------------------------------
# Testing (runs against .env.local DB)
# -------------------------------
test: ## Run tests with rollback isolation (using .env.local DB)
	$(MAKE) clean ENV_FILE=.env.local
	$(COMPOSE) up --build -d
	$(MAKE) migrate ENV_FILE=.env.local
	$(COMPOSE) exec -T backend pytest -v
	$(MAKE) clean ENV_FILE=.env.local

ci-test: ## CI mode: reset, abort on exit, propagate exit code
	$(MAKE) clean ENV_FILE=.env.local
	$(COMPOSE) up --build --abort-on-container-exit --exit-code-from backend
	$(MAKE) clean ENV_FILE=.env.local

# -------------------------------
# Utilities
# -------------------------------
logs: ## Tail logs for all services
	$(COMPOSE) logs -f

logs-backend: ## Tail logs only for backend
	$(COMPOSE) logs -f backend

logs-db: ## Tail logs only for database
	$(COMPOSE) logs -f db

logs-once: ## Show logs once for backend
	$(COMPOSE) logs backend

shell: ## Open shell in backend
	$(COMPOSE) exec backend bash

# -------------------------------
# Production (with .env.prod)
# -------------------------------
prod-up: ## Start stack with .env.prod
	$(MAKE) up ENV_FILE=.env.prod

prod-down: ## Stop stack (keep volumes) with .env.prod
	$(MAKE) down ENV_FILE=.env.prod

prod-clean: ## Stop stack and remove volumes with .env.prod
	$(MAKE) clean ENV_FILE=.env.prod

prod-migrate: ## Run migrations with .env.prod
	$(MAKE) migrate ENV_FILE=.env.prod