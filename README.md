# tracelink

tracelink is an asynchronous URL-shortening API with built-in click analytics. It creates compact, shareable links, redirects visitors to their original destinations, and records privacy-conscious events that can be queried as aggregate statistics.

The project is designed as a controlled, portfolio-grade MVP with clear architectural boundaries, reproducible dependency management, automated database migrations, and a production-oriented quality workflow.

## Live API

- Web interface: <https://tracelink-xmd8.onrender.com/>

- API: <https://tracelink-xmd8.onrender.com>
- Swagger UI: <https://tracelink-xmd8.onrender.com/docs>
- Health: <https://tracelink-xmd8.onrender.com/health>
- Readiness: <https://tracelink-xmd8.onrender.com/ready>

The API runs on Render and uses a Neon PostgreSQL database in AWS Frankfurt. The free Render instance can spin down during inactivity, so the first request after an idle period may take longer.

## Tech Stack

| Technology | Role |
| --- | --- |
| Python 3.14 | Application language and async runtime |
| [uv](https://docs.astral.sh/uv/) | Python version, virtual environment, dependency, and lockfile management |
| [FastAPI](https://fastapi.tiangolo.com/) | ASGI web framework and OpenAPI documentation |
| [Pydantic v2](https://docs.pydantic.dev/) | Request, response, and settings validation |
| [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) | Async ORM and database access layer |
| [PostgreSQL](https://www.postgresql.org/) | Primary relational database |
| [asyncpg](https://magicstack.github.io/asyncpg/current/) | Async PostgreSQL driver |
| [Alembic](https://alembic.sqlalchemy.org/) | Database schema migrations |
| [pytest](https://docs.pytest.org/) | Unit, integration, and API testing |
| [Ruff](https://docs.astral.sh/ruff/) | Linting, import sorting, and formatting |
| [ty](https://docs.astral.sh/ty/) | Static type checking |
| Docker Compose | Reproducible local PostgreSQL service |

## Architecture

tracelink follows a Router-Service-Repository architecture:

```text
HTTP request
    |
    v
FastAPI router        HTTP concerns and schema validation
    |
    v
Service               Business rules and transaction orchestration
    |
    v
Repository            Persistence queries
    |
    v
SQLAlchemy AsyncSession
    |
    v
PostgreSQL
```

- **Routers** translate HTTP requests into application operations and return validated responses.
- **Services** implement link creation, expiration, redirect, and analytics rules.
- **Repositories** isolate SQLAlchemy queries and persistence behavior.
- **Schemas** define the public API contract independently from ORM models.
- **Models** represent the relational database structure.
- **Core modules** contain settings, logging, and shared exception behavior.

Each request receives its own `AsyncSession`. Sessions are never shared between concurrent tasks.

## Project Structure

```text
tracelink/
|-- src/
|   `-- tracelink/
|       |-- __init__.py
|       |-- main.py
|       |-- api/
|       |   |-- __init__.py
|       |   |-- dependencies.py
|       |   `-- v1/
|       |       |-- __init__.py
|       |       |-- router.py
|       |       `-- endpoints/
|       |           |-- __init__.py
|       |           |-- analytics.py
|       |           |-- health.py
|       |           |-- links.py
|       |           `-- redirects.py
|       |-- core/
|       |   |-- __init__.py
|       |   |-- config.py
|       |   |-- exceptions.py
|       |   `-- logging.py
|       |-- db/
|       |   |-- __init__.py
|       |   |-- base.py
|       |   |-- session.py
|       |   `-- models/
|       |       |-- __init__.py
|       |       |-- click_event.py
|       |       `-- link.py
|       |-- repositories/
|       |   |-- __init__.py
|       |   |-- click_event.py
|       |   `-- link.py
|       |-- schemas/
|       |   |-- __init__.py
|       |   |-- analytics.py
|       |   |-- common.py
|       |   `-- link.py
|       |-- services/
|       |   |-- __init__.py
|       |   |-- analytics.py
|       |   |-- link.py
|       |   `-- redirect.py
|       `-- utils/
|           |-- __init__.py
|           `-- short_code.py
|-- migrations/
|   |-- versions/
|   |-- env.py
|   `-- script.py.mako
|-- tests/
|   |-- conftest.py
|   |-- unit/
|   |   |-- services/
|   |   `-- utils/
|   `-- integration/
|       |-- api/
|       `-- repositories/
|-- .env.example
|-- .gitignore
|-- .python-version
|-- alembic.ini
|-- compose.yaml
|-- Dockerfile
|-- Makefile
|-- pyproject.toml
|-- README.md
`-- uv.lock
```

## MVP Features

### API routes

- [x] `POST /api/v1/links` creates a short link.
- [ ] `GET /api/v1/links/{link_id}` returns link metadata.
- [ ] `PATCH /api/v1/links/{link_id}` updates expiration or active state.
- [x] `GET /api/v1/links/{slug}/stats` returns aggregate click analytics.
- [x] `GET /{short_code}` records a click and returns a `307 Temporary Redirect`.
- [x] `GET /health` reports process health.
- [x] `GET /ready` verifies database readiness.

### Business rules

- [x] Accept only valid `http` and `https` destination URLs.
- [x] Generate URL-safe, collision-resistant short codes.
- [x] Allow optional custom aliases while rejecting reserved routes.
- [x] Enforce short-code uniqueness in PostgreSQL.
- [x] Support optional expiration timestamps.
- [ ] Disable links without deleting their historical analytics.
- [x] Record timestamp, referrer, user agent, and an optional privacy-preserving IP hash.
- [ ] Return analytics grouped by day, referrer, and user agent.
- [x] Use timezone-aware UTC timestamps throughout the application.
- [x] Treat click events as the analytics source of truth.

## Getting Started

### Prerequisites

Install the following tools before continuing:

- Python 3.14
- `uv`
- Docker Desktop or another Docker-compatible runtime with Compose support
- Git

Verify the local toolchain:

```bash
python3 --version
uv --version
docker --version
docker compose version
git --version
```

### 1. Clone and enter the repository

```bash
git clone git@github.com:medioalanum/tracelink.git
cd tracelink
```

If you are working from an existing local checkout, enter it directly:

```bash
cd /Users/alanviana/Projects/tracelink
```

### 2. Install the project environment

The committed `.python-version`, `pyproject.toml`, and `uv.lock` define the expected environment.

```bash
uv python install
uv sync
```

`uv sync` creates the local `.venv` when necessary and installs both runtime and default development dependencies.

### 3. Configure environment variables

Create a local environment file from the committed template:

```bash
cp .env.example .env
```

The expected local database URL is:

```dotenv
DATABASE_URL=postgresql+asyncpg://tracelink:tracelink@localhost:5432/tracelink
```

Do not commit `.env` or any production credentials.

### 4. Start PostgreSQL

```bash
docker compose up -d postgres
docker compose ps
```

Wait until the PostgreSQL service is healthy before applying migrations.

### 5. Apply database migrations

```bash
uv run alembic upgrade head
```

Create a migration after intentionally changing the SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
```

Always review autogenerated migrations before applying or committing them.

### 6. Run the API

```bash
uv run uvicorn tracelink.main:app --reload
```

The local application will be available at:

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

### 7. Stop local infrastructure

```bash
docker compose down
```

To also remove the local PostgreSQL volume and all local database data:

```bash
docker compose down --volumes
```

The volume-removal command is destructive and should only be used when the local database can be safely recreated.

## Testing

Run the complete test suite:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=tracelink --cov-report=term-missing
```

Run only unit or integration tests:

```bash
uv run pytest tests/unit
uv run pytest tests/integration
```

Integration tests should run against PostgreSQL rather than SQLite so that constraints, transactions, and async driver behavior match the production database.

## Code Quality

Check lint rules:

```bash
uv run ruff check .
```

Apply safe automatic lint fixes:

```bash
uv run ruff check . --fix
```

Format the codebase:

```bash
uv run ruff format .
```

Verify formatting without changing files:

```bash
uv run ruff format --check .
```

Run static type checking:

```bash
uv run ty check
```

Run the complete local quality gate before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov=tracelink --cov-report=term-missing
```

## Data and Privacy

tracelink should not store raw IP addresses. If approximate unique-visitor reporting is enabled, addresses should be transformed using a keyed, rotating hash before persistence. Production deployments should also define retention limits for click events and document their privacy behavior.

## API Documentation

FastAPI generates an OpenAPI document from the application's routes and Pydantic schemas. When the API is running locally, use `/docs` for interactive exploration and `/openapi.json` for the machine-readable contract.

## Roadmap

- [ ] Add user accounts, authentication, and per-owner link management.
- [ ] Add Redis-backed caching and distributed rate limiting.
- [ ] Add custom domains and verified domain ownership.
- [ ] Add geographic enrichment, bot filtering, and an analytics dashboard with configurable retention.

## License

No license has been selected yet. Until a license is added, the repository remains under the default protections of copyright law.
