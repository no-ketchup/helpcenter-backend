# Default environment file
ENV_FILE ?= .env

# Compose base command
COMPOSE = docker compose --env-file $(ENV_FILE)

# Build containers
build:
	$(COMPOSE) build

# Start stack in background
up:
	$(COMPOSE) up -d

# Stop stack and clean up
down:
	$(COMPOSE) down --volumes --remove-orphans

# Run migrations
migrate:
	$(COMPOSE) run --rm backend alembic upgrade head

# Run tests (always reset DB volume)
test:
	$(COMPOSE) down -v --remove-orphans
	$(COMPOSE) up --build -d
	$(COMPOSE) exec -T backend alembic upgrade head
	$(COMPOSE) exec -T backend pytest -v
	$(COMPOSE) down -v --remove-orphans

# Run tests like CI (always reset, aborts on exit)
ci-test:
	$(COMPOSE) down -v --remove-orphans
	ENV_FILE=.env.test $(COMPOSE) up --build --abort-on-container-exit
	ENV_FILE=.env.test $(COMPOSE) down --volumes --remove-orphans

# Tail logs
logs:
	$(COMPOSE) logs -f

# Open shell inside backend container
shell:
	$(COMPOSE) exec backend bash

# Production deploy (NeonDB)
prod-up:
	ENV_FILE=.env.prod $(COMPOSE) up -d

prod-down:
	ENV_FILE=.env.prod $(COMPOSE) down --volumes --remove-orphans

prod-migrate:
	ENV_FILE=.env.prod $(COMPOSE) run --rm backend alembic upgrade head