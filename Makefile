.PHONY: help setup start stop restart status logs logs-app health shell format lint type-check test test-cov pre-commit clean prune migrate-gen migrate-up migrate-down db-status

# Variables
PYTHON_DIRS := app modules shared worker tests
TYPE_DIRS := app modules shared worker
ALEMBIC := uv run alembic

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Install Python dependencies with uv
	uv sync

start: ## Build and start all Docker services
	docker compose up --build -d

stop: ## Stop and remove Docker services
	docker compose down

restart: ## Restart Docker services
	docker compose restart

status: ## Show Docker service status
	docker compose ps

logs: ## Follow logs for all services
	docker compose logs -f

logs-app: ## Follow application logs
	docker compose logs -f app

health: ## Check application and Docker service health
	@echo "Checking application health..."
	@curl -fsS http://localhost:8000/health || echo "API not responding"
	@echo ""
	@docker compose ps

shell: ## Open shell inside app container
	docker compose exec app sh

# --- Code Quality ---
format: ## Format Python code with Ruff
	uv run ruff format $(PYTHON_DIRS)

lint: ## Lint Python code with Ruff
	uv run ruff check $(PYTHON_DIRS) --fix

type-check: ## Run type checking with mypy
	uv run mypy $(TYPE_DIRS)

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=app --cov=modules --cov=shared --cov=worker --cov-report=term-missing --cov-report=html

pre-commit: ## Run all pre-commit hooks on all files
	uv run pre-commit run --all-files

# --- Database & Migrations ---
migrate-gen: ## Generate a new migration file (usage: make migrate-gen m="description")
	$(ALEMBIC) revision --autogenerate -m "$(m)"

migrate-up: ## Upgrade database to the latest version
	$(ALEMBIC) upgrade head

migrate-down: ## Rollback database one version
	$(ALEMBIC) downgrade -1

db-status: ## Show current migration status of the database
	$(ALEMBIC) current

# --- Cleanup ---
clean: ## Stop services and remove project volumes
	docker compose down -v

prune: ## Remove unused Docker resources
	docker system prune -f

### snakeviz
snakeviz:
	uv run snakeviz profiles/${m}