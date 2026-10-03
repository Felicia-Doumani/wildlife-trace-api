# WildTrace API

WildTrace is a containerized REST API for recording and retrieving wildlife sightings.

The project is built as a production-style backend and DevOps application with a focus on API development, containerization, automated testing, database migrations, asynchronous task processing, code quality, security checks, and CI/CD practices.

## Tech Stack

- **Python 3.12**
- **FastAPI** — REST API framework
- **PostgreSQL 16** — relational database
- **SQLAlchemy 2.0** — ORM and database access
- **Alembic** — database migrations
- **Pydantic** — request and response validation
- **Redis 7** — message broker for asynchronous task processing
- **Celery** — background task processing
- **Docker & Docker Compose** — containerized development and multi-service environment
- **Pytest** — automated testing
- **Ruff** — linting
- **pip-audit** — Python dependency vulnerability scanning
- **GitHub Actions** — continuous integration

## Features

WildTrace currently provides:

- Create wildlife sightings
- Retrieve all sightings
- Retrieve individual sightings by ID
- Update existing sightings
- Delete sightings
- Filter sightings by species
- Filter sightings by observation date range
- Pagination with `skip` and `limit`
- Input validation for coordinates, URLs, dates, and required fields
- PostgreSQL persistence
- Versioned database migrations with Alembic
- Redis-backed asynchronous task queue
- Separate Celery background worker
- Health and readiness endpoints
- Dockerized multi-service infrastructure
- Automated API testing
- Test coverage enforcement
- Automated linting
- Dependency vulnerability scanning
- Automated Docker image builds in CI

## Architecture

WildTrace runs as a multi-service application:

```text
                     ┌──────────────┐
                     │    Client    │
                     └──────┬───────┘
                            │ HTTP
                            ▼
                     ┌──────────────┐
                     │   FastAPI    │
                     └──────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │  PostgreSQL  │      │    Redis     │
          └──────────────┘      └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │Celery Worker │
                               └──────────────┘
```

When a sighting is created, FastAPI stores the record in PostgreSQL and queues a background processing task through Redis. A separate Celery worker consumes and executes the task asynchronously.

The API and Celery worker run as separate Docker services while sharing the same application code and Docker image.

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

Create a sighting:

```http
POST /api/v1/sightings
```

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

Filtering and pagination are supported through query parameters such as:

```http
GET /api/v1/sightings?species=seal
```

```http
GET /api/v1/sightings?observed_from=2026-10-01T00:00:00Z&observed_to=2026-10-31T23:59:59Z
```

```http
GET /api/v1/sightings?skip=0&limit=20
```

Retrieve a specific sighting:

```http
GET /api/v1/sightings/{sighting_id}
```

Update a sighting:

```http
PATCH /api/v1/sightings/{sighting_id}
```

Delete a sighting:

```http
DELETE /api/v1/sightings/{sighting_id}
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

Docker Compose starts:

- FastAPI application
- PostgreSQL development database
- PostgreSQL test database
- Redis
- Celery worker

Check running services:

```bash
docker compose ps
```

The API is available at:

```text
http://localhost:8000
```

FastAPI's interactive API documentation is available at:

```text
http://localhost:8000/docs
```

## Background Processing

WildTrace uses Redis and Celery for asynchronous background task processing.

When a sighting is successfully created and committed to PostgreSQL, the API queues a Celery task:

```text
POST /api/v1/sightings
        │
        ▼
     FastAPI
        │
        ▼
   PostgreSQL
        │
        ▼
      Redis
        │
        ▼
 Celery Worker
```

This separates HTTP request handling from work that can be performed independently by a background worker.

During automated API tests, Celery task dispatch is mocked. This keeps the test suite independent of Redis and the worker while still verifying that sighting creation queues the expected background task.

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

WildTrace has automated API tests covering CRUD operations, validation, filtering, and background task dispatch.

Run the tests locally:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest -v --cov=app --cov-report=term-missing
```

The CI pipeline requires at least **85% test coverage**.

## Code Quality

Run Ruff:

```bash
ruff check .
```

Ruff is executed automatically by the CI pipeline to detect Python code-quality issues before changes are accepted.

## Security

Python dependencies can be checked for known vulnerabilities with:

```bash
pip-audit -r requirements.txt
```

Dependency auditing is also performed automatically by the CI pipeline.

Container image vulnerability scanning is planned as the next security step.

## Continuous Integration

GitHub Actions automatically validates pushes and pull requests.

The current pipeline performs:

1. Dependency installation
2. Database migration execution
3. Ruff linting
4. Python dependency vulnerability scanning
5. Pytest execution
6. Coverage enforcement
7. Docker image build

A failed migration, quality, test, security, or build check causes the workflow to fail.

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
│   │   ├── celery_app.py
│   │   └── tasks.py
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

The current foundation includes:

- REST API with CRUD operations and filtering
- PostgreSQL persistence
- Alembic database migrations
- Redis and Celery background processing
- Multi-service Docker Compose environment
- Automated testing and coverage enforcement
- Linting and dependency auditing
- GitHub Actions CI
- Automated Docker image builds

### DevOps Roadmap

Planned next steps:

1. **Container security scanning** — scan built Docker images for known vulnerabilities using Trivy.
2. **Container registry** — publish validated, versioned images to GitHub Container Registry (GHCR).
3. **Deployment** — run WildTrace in a remote/cloud environment with an automated deployment workflow.
4. **Kubernetes** — deploy and manage the containerized application as Kubernetes workloads.
5. **Terraform** — provision infrastructure using Infrastructure as Code.
6. **Observability** — introduce application and infrastructure monitoring with Prometheus and Grafana.

## Purpose

WildTrace was created as a backend and DevOps engineering portfolio project demonstrating how a Python API can progress beyond basic CRUD functionality into a tested, containerized, migration-managed, asynchronously processed, and continuously validated application.

The long-term goal is to demonstrate the full path from application development to CI/CD, container security, deployment, infrastructure management, orchestration, and observability.