# WildTrace API

WildTrace is a containerized REST API for recording and retrieving wildlife sightings.

The project is built as a production-style backend application with a focus on API development, containerization, automated testing, database migrations, code quality, security checks, and CI/CD practices.

## Tech Stack

- **Python 3.12**
- **FastAPI** — REST API framework
- **PostgreSQL 16** — relational database
- **SQLAlchemy 2.0** — ORM and database access
- **Alembic** — database migrations
- **Pydantic** — request and response validation
- **Redis** — infrastructure for asynchronous/background processing
- **Docker & Docker Compose** — containerized development environment
- **Pytest** — automated testing
- **Ruff** — linting
- **pip-audit** — Python dependency vulnerability scanning
- **GitHub Actions** — continuous integration

## Features

WildTrace currently provides:

- Create wildlife sightings
- Retrieve all sightings
- Retrieve individual sightings by ID
- Input validation for coordinates, URLs, and required fields
- PostgreSQL persistence
- Versioned database migrations with Alembic
- Health and readiness endpoints
- Dockerized application infrastructure
- Automated API testing
- Test coverage enforcement
- Automated linting
- Dependency vulnerability scanning
- Automated Docker image builds in CI

## Sighting Model

Each wildlife sighting contains:

| Field | Description |
| --- | --- |
| `id` | Unique sighting identifier |
| `species` | Species observed |
| `latitude` | Observation latitude |
| `longitude` | Observation longitude |
| `observed_at` | Time the animal was observed |
| `photo_url` | Optional URL to a photo |
| `notes` | Optional observation notes |
| `created_at` | Time the record was created |

## API Endpoints

### Health

```http
GET /healthz
```

Checks whether the API process is running.

```http
GET /readyz
```

Checks whether the API can connect to PostgreSQL.

### Sightings

```http
POST /api/v1/sightings
```

Creates a new wildlife sighting.

Example request:

```json
{
  "species": "Mediterranean monk seal",
  "latitude": 37.75,
  "longitude": 26.98,
  "observed_at": "2026-10-01T15:30:00Z",
  "photo_url": "https://example.com/monk-seal.jpg",
  "notes": "Observed swimming near the coastline."
}
```

Retrieve sightings:

```http
GET /api/v1/sightings
```

Pagination is supported through `skip` and `limit` query parameters.

Retrieve a specific sighting:

```http
GET /api/v1/sightings/{sighting_id}
```

A request for a nonexistent sighting returns `404 Not Found`.

## Running Locally

### Requirements

Install:

- Docker
- Docker Compose

Clone the repository and start the services:

```bash
git clone <repository-url>
cd wildtrace
docker compose up --build -d
```

Docker Compose starts the API, PostgreSQL, Redis, and the test PostgreSQL service.

The API is available at:

```text
http://localhost:8000
```

FastAPI's interactive API documentation is available at:

```text
http://localhost:8000/docs
```

## Database Migrations

Database schema changes are managed with Alembic rather than being created automatically when the API starts.

Apply all migrations:

```bash
docker compose exec api alembic upgrade head
```

Check the current migration:

```bash
docker compose exec api alembic current
```

Create a migration after changing the SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
```

Generated migrations are stored under:

```text
alembic/versions/
```

## Testing

WildTrace has automated API tests covering the primary sighting endpoints and validation behavior.

Run the tests locally:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest -v --cov=app --cov-report=term-missing
```

The CI pipeline currently requires at least **85% test coverage**.

## Code Quality

Run Ruff:

```bash
ruff check .
```

The project uses Ruff as part of the CI pipeline to detect Python code-quality issues before changes are accepted.

## Security

Python dependencies can be checked for known vulnerabilities with:

```bash
pip-audit -r requirements.txt
```

Dependency auditing is also performed automatically by the CI pipeline.

## Continuous Integration

GitHub Actions automatically validates pushes and pull requests.

The current pipeline performs:

1. Dependency installation
2. Ruff linting
3. Python dependency vulnerability scanning
4. Pytest execution
5. Coverage enforcement
6. Docker image build

A failed quality, test, security, or build check causes the workflow to fail.

## Project Structure

```text
wildtrace/
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── routers/
│   │   └── sightings.py
│   ├── workers/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── conftest.py
│   └── test_sightings.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

## Development Status

WildTrace is under active development.

The current backend foundation includes the REST API, PostgreSQL persistence, migrations, Docker infrastructure, automated tests, linting, dependency auditing, and CI.

Planned improvements include:

- Container vulnerability scanning
- Publishing versioned Docker images to a container registry
- Redis-backed background processing
- Additional API functionality
- Deployment automation
- Kubernetes deployment configuration

## Purpose

WildTrace was created as a backend and DevOps engineering project demonstrating how a Python API can progress beyond basic CRUD functionality into a tested, containerized, migration-managed, and continuously validated application.