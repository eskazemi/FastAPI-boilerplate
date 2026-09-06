# FastAPI Boilerplate

A production-oriented FastAPI boilerplate designed for building maintainable, testable, and infrastructure-friendly backend services.

This project combines a modular monolith architecture with Clean Architecture principles, async SQLAlchemy, Redis caching, structured exception handling, health checks, and environment-based configuration.

It is intentionally kept simple so that teams can use it as a practical starting point and extend it according to their business and infrastructure requirements.

## Features

- FastAPI application factory
- Explicit application bootstrap and dependency wiring
- Modular monolith architecture
- Clean separation between domain, application, and infrastructure layers
- Async SQLAlchemy integration
- PostgreSQL support
- Repository Pattern
- Unit of Work Pattern
- Dependency-based database session management
- Alembic-ready database migration structure
- Redis-based caching
- Pluggable cache backend and cache key generation
- Tag-based cache invalidation
- JSON-safe cache serialization
- Fail-safe cache behavior when Redis is unavailable
- Structured API exception responses
- Authentication middleware based on Starlette-compatible backends
- Response metadata logging without logging sensitive response bodies
- CORS configuration through application settings
- Liveness and readiness health checks
- Async testing setup with Pytest and `pytest_asyncio`
- Environment-based configuration with Pydantic Settings
- Ruff for linting and formatting
- `uv` for dependency and environment management
- Python 3.11 target

## Architecture

The project follows a modular monolith architecture.

Each business module owns its own application, domain, and infrastructure responsibilities. Shared technical concerns such as configuration, database access, caching, middleware, exception handling, and HTTP infrastructure are kept under the shared layer.

The application is created and wired in `app/bootstrap.py`, while `app/main.py` exposes the final ASGI application.
```text
app/
├── bootstrap.py          # Application wiring and configuration
└── main.py               # ASGI application entrypoint

modules/
└── account/              # Example business module
├── application/      # Use cases, commands, handlers, schemas
├── domain/           # Entities, repository contracts, exceptions
└── infrastructure/   # FastAPI routes, database models, repositories

shared/
├── cache/                # Cache manager, Redis backend, key maker, tags
├── config.py             # Application settings
├── infrastructure/       # Database and shared HTTP infrastructure
└── middlewares/          # Authentication and response logging

tests/
└── conftest.py           # Async fixtures and test database setup
```
## Clean Architecture Layers

### Domain

The domain layer contains the core business concepts and rules.

Typical responsibilities include:

- Entities
- Value objects
- Repository protocols
- Domain exceptions
- Business rules

The domain layer should not depend on FastAPI, SQLAlchemy, Redis, or other infrastructure tools.

### Application

The application layer coordinates business operations and use cases.

Typical responsibilities include:

- Commands
- Query objects
- Use-case handlers
- Application schemas
- Transaction orchestration

This layer depends on domain contracts rather than concrete infrastructure implementations.

### Infrastructure

The infrastructure layer contains framework and technology-specific implementations.

Typical responsibilities include:

- FastAPI routes
- SQLAlchemy models
- Repository implementations
- Database session management
- Middleware
- External service integrations

This separation makes it easier to test business logic and replace infrastructure components without rewriting the domain.

## Request Flow

A typical request flows through the following stages:

text
HTTP Request
↓
FastAPI Route
↓
Request Validation
↓
Application Command or Query
↓
Handler
↓
Domain Logic
↓
Repository
↓
Unit of Work
↓
Async SQLAlchemy
↓
PostgreSQL
↓
HTTP Response

The route layer is responsible for HTTP concerns. Business decisions remain inside the application and domain layers.

## Application Bootstrap

Application wiring is centralized in `app/bootstrap.py`.

python
from app.bootstrap import create_app

app = create_app()

The ASGI entrypoint is exposed from `app/main.py`:

python
from app.bootstrap import create_app

app = create_app()

Keeping startup logic in one place makes the application easier to understand, test, and extend.

## Database

The project uses:

- PostgreSQL
- Async SQLAlchemy
- Dependency-based database sessions
- Repository Pattern
- Unit of Work Pattern
- Alembic for database migrations

Database sessions are managed explicitly through dependencies and transaction boundaries. They are not hidden inside global middleware.

This provides:

- Clear transaction ownership
- Better testability
- Easier rollback handling
- Separation between business logic and persistence details

## Caching

The cache layer is based on Redis and is organized around pluggable components:

- `CacheManager`
- `RedisBackend`
- Custom cache key maker
- `CacheTag`
- JSON-safe serialization

Example:

```python
from shared.cache.cache_manager import Cache
from shared.cache.cache_tag import CacheTag


@Cache.cached(tag=CacheTag.GET_USER_LIST, ttl=300)
async def get_users():
...
```
Cached data can be invalidated by tag:

```python
await Cache.remove_by_tag(CacheTag.GET_USER_LIST)
```
The cache layer is designed to fail safely. If Redis is unavailable or the cache has not been initialized, the application can continue to operate without turning a cache failure into an application failure.

The implementation uses JSON-compatible serialization instead of unsafe serializers such as `pickle`.

## Health Checks

The application provides two health endpoints:

text
GET /health/live
GET /health/ready

### Liveness

`/health/live` verifies that the application process is running.

### Readiness

`/health/ready` verifies that the application is ready to serve traffic. This includes a database connectivity check using:

```sql
SELECT 1;
```
These endpoints can be connected to container or Kubernetes health probes.

## Middleware

The boilerplate includes the following middleware components:

### Authentication Middleware

Authentication is implemented using a Starlette-compatible authentication backend.

The concrete authentication strategy can be customized according to the application requirements.

### Response Logging Middleware

The response logger records request and response metadata without logging response bodies.

This approach reduces the risk of exposing:

- Passwords
- Access tokens
- Personal data
- Large response payloads
- Other sensitive information

### CORS Middleware

 Middleware

CORS behavior is configured through application settings rather than being hard-coded definitions.

## Configuration

Application configuration is managed through Pydantic Settings and environment variables.

Example Redis configuration:

```python
REDIS_URL = "redis://localhost:6379/7"
```
When passing validated Pydantic DSN values to libraries that expect a plain string, convert them explicitly:
```
 DSN objects.from_url(str(config.REDIS_URL))
```
This avoids type mismatches between validated DSN objects and third-party clients.

Before using the project in production, review and define the complete configuration contract for:

- Database connection
- Redis connection
- Authentication
- CORS
- Application environment
- Logging
- Secret values

## Requirements

- Python 3.12+
- PostgreSQL
- Redis
- `uv`

Install `uv` by following the official documentation:

<https://docs.astral.sh/uv/>

## Installation

Clone the repository:

```bash
git clone https://github.com/eskazemi/FastAPI-boilerplate.git
cd FastAPI-boilerplate
```
Install dependencies:

```bash
uv sync
```
Create the required environment configuration according to the settings defined in the project.

## Running Locally

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```
The API will be available at:

```text
http://127.0.0.1:8000
```
FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```
Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```
## Database Migrations

The project is structured to use Alembic for database migrations.

Typical commands:

```bash
uv run alembic upgrade head
```
Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```
Review generated migrations carefully before applying them to any shared or production database.

## Testing

Run the test suite with:

```bash
uv run pytest
```
The test setup uses `pytest_asyncio` for asynchronous fixtures.

Database-related tests are designed around isolated transactions and cleanup logic so that repeated test runs do not leave unwanted persistent state.

## Code Quality

The project uses Ruff for linting and formatting.

Run lint checks:

```bash
uv run ruff check .
```
Apply automatic lint fixes:

```bash
uv run ruff check . --fix
```
Format the code:

```bash
uv run ruff format .
```
The current Ruff configuration targets Python 3.11 and uses a maximum line length of 100 characters.

The configured rule families include:

```text
E, W, F, I, UP, B, C4, SIM, PT, RUF
```
## Design Principles

This project is based on the following principles:

- Keep business logic independent from frameworks
- Make transaction boundaries explicit
- Prefer contracts over concrete implementations
- Keep technical concerns inside infrastructure
- Make application wiring visible and centralized
- Keep cache failures from breaking core application behavior
- Avoid logging sensitive response payloads
- Prefer simple and understandable abstractions
- Make the project easy to test and extend

## Production Considerations

This repository is a starting point, not a complete production platform.

Before deploying it to a production environment, consider adding or reviewing:

- HTTPS termination
- Secret management
- Strict CORS configuration
- Rate limiting
- Request ID propagation
- Structured JSON logging
- Metrics and distributed tracing
- Background job processing
- Database backup and recovery
- Database connection pool tuning
- Redis availability and eviction policies
- Kubernetes security controls
- Network policies
- Resource requests and limits
- Graceful shutdown behavior
- Dependency and image vulnerability scanning
- CI/CD pipelines

The correct production configuration depends on the workload, traffic pattern, deployment platform, and operational requirements of each organization.

## Project Status

This project is intentionally simple and opinionated.

It provides a clean foundation for starting a FastAPI service, but every real-world system may require additional modules, integrations, observability, security controls, and deployment automation.

Feedback, issues, and improvements are welcome.

## License

Add the license that matches your project before publishing or distributing the repository.

