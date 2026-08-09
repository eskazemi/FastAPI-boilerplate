# FastAPI Boilerplate

A production-oriented FastAPI boilerplate built with Clean Architecture, modular monolith principles, async SQLAlchemy, structured exception handling, Redis caching, and health checks.

This project is designed as a practical starting point for backend services that need clear boundaries, testability, maintainability, and infrastructure-friendly behavior from day one.

## Features

- FastAPI application factory and bootstrap-based wiring
- Modular monolith structure
- Clean separation between application, domain, infrastructure, and shared layers
- Async SQLAlchemy with Unit of Work pattern
- Dependency-based database session management
- Structured API exception responses
- Redis-based cache manager with pluggable backend and key maker
- JSON-safe cache serialization
- Fail-safe cache behavior when Redis is unavailable
- Authentication middleware based on Starlette-compatible backends
- Response logging middleware focused on metadata, not sensitive payloads
- Liveness and readiness health checks
- Pytest async test setup
- Environment-based configuration with Pydantic settings

## Project Structure
```text
app/
  bootstrap.py        # Application wiring, middleware, routers, cache, exception handlers
  main.py             # ASGI entrypoint

modules/
  account/            # Example business module
application/
domain/
infrastructure/

shared/
  cache/              # Cache manager, Redis backend, key maker, cache tags
  config.py           # Application configuration
  infrastructure/     # Database, HTTP routes, exception handlers
  middlewares/        # Authentication and response logging middleware

tests/
  conftest.py         # Async pytest fixtures and database cleanup
```
## Architecture

The project follows a modular monolith approach.

Each business module owns its own application, domain, and infrastructure code. Shared technical concerns such as configuration, caching, database infrastructure, middleware, and exception handling live under the `shared` package.

The application is wired from `app/bootstrap.py`, while `app/main.py` only exposes the final ASGI application.

python
from app.bootstrap import create_app

app = create_app()

This keeps startup logic explicit and avoids spreading framework configuration across the codebase.

## Exception Handling

API errors use a consistent JSON response shape:

json
{
  "status": 400,
  "message": "Bad request",
  "detail": "Invalid input",
  "timestamp": "2026-08-09T12:00:00Z"
}

Custom exceptions inherit from a shared base exception and expose an HTTP status code. Exception handlers are registered centrally during application bootstrap.

## Database

The project uses async SQLAlchemy and manages database sessions through dependency injection and the Unit of Work pattern.

Database sessions are not managed by global middleware. This makes transaction boundaries explicit, testable, and easier to reason about.

## Cache

Caching is provided through a singleton `CacheManager` and pluggable components:

- `RedisBackend` for Redis storage
- `CustomKeyMaker` for deterministic cache keys
- `CacheTag` for tag-based invalidation

Example usage:

python
from shared.cache.cache_manager import Cache
from shared.cache.cache_tag import CacheTag


@Cache.cached(tag=CacheTag.GET_USER_LIST, ttl=300)
async def get_users():
...

Invalidate cached data by tag:

python
await Cache.remove_by_tag(CacheTag.GET_USER_LIST)

The cache layer uses JSON serialization instead of pickle and is designed to fail safely. If Redis is unavailable or cache is not initialized, application logic can continue without crashing.

## Health Checks

The project exposes two health endpoints:

text
GET /health/live
GET /health/ready

`/health/live` verifies that the application process is running.

`/health/ready` verifies that the application is ready to serve traffic, including a database connectivity check using `SELECT 1`.

These endpoints are suitable for Kubernetes liveness and readiness probes.

## Middleware

The boilerplate includes:

- `AuthenticationMiddleware` using a Starlette-compatible authentication backend
- `ResponseLoggerMiddleware` for request/response metadata logging
- CORS middleware configured from application settings

The response logger intentionally avoids logging response bodies to reduce the risk of leaking sensitive data.

## Configuration

Configuration is handled through Pydantic settings.

Example Redis configuration:

python
REDIS_URL: RedisDsn = "redis://localhost:6379/7"

When passing validated DSN values to third-party libraries, convert them to plain strings:

python
Redis.from_url(str(config.REDIS_URL))

This avoids type mismatch issues between Pydantic DSN objects and libraries that expect `str` URLs.

## Development

Install dependencies:

bash
uv sync

Run the application:

bash
uv run uvicorn app.main:app --reload

Run tests:

bash
uv run pytest

## Testing

The test setup uses `pytest_asyncio` for async fixtures.

Database tests are isolated through transaction rollback and database cleanup logic, so tests can run repeatedly without leaving persistent state behind.

## Security Notes

This boilerplate avoids unsafe cache serialization such as `pickle` and prefers JSON-compatible payloads.

Logging middleware is designed to avoid recording sensitive response bodies.

For production deployments, consider enabling:

- HTTPS termination
- secure secret management
- API server and application audit logging
- stricter CORS configuration
- rate limiting
- request ID propagation
- structured JSON logging
- Kubernetes security controls and network policies

## License

Add your preferred license before publishing.
