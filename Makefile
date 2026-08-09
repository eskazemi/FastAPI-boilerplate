.PHONY: help setup start stop restart status logs logs-app health shell format lint type-check test test-cov pre-commit clean prune

PYTHON_DIRS := app modules shared worker tests
TYPE_DIRS := app modules shared worker

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

clean: ## Stop services and remove project volumes
	docker compose down -v

prune: ## Remove unused Docker resources
	docker system prune -f
