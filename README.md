# WildTrace API

WildTrace is a containerized REST API for recording, managing, and retrieving wildlife sightings.

The project is built as a backend and DevOps portfolio project demonstrating the complete path from application development to automated testing, containerization, security scanning, container publishing, and cloud deployment.

WildTrace is currently deployed on **AWS EC2**, where the API, PostgreSQL database, Redis broker, and Celery worker run as separate Docker containers.

---

## Tech Stack

### Backend

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy 2.0
- Psycopg 3
- PostgreSQL 16
- Alembic

### Background Processing

- Redis 7
- Celery

### Testing & Code Quality

- Pytest
- pytest-cov
- Ruff

### Security

- pip-audit
- Trivy

### DevOps & Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- GitHub Container Registry (GHCR)
- AWS EC2
- AWS EBS
- AWS Security Groups

---

## Features

WildTrace currently supports:

- Creating wildlife sightings
- Retrieving all sightings
- Retrieving individual sightings by ID
- Updating existing sightings
- Deleting sightings
- Filtering sightings by species
- Filtering sightings by observation date range
- Pagination using `skip` and `limit`
- Request and response validation
- PostgreSQL persistence
- Version-controlled database migrations
- Redis-backed asynchronous task queuing
- Celery background processing
- Health and readiness endpoints
- Automated API testing
- Test coverage enforcement
- Automated linting
- Dependency vulnerability scanning
- Container vulnerability scanning
- Automated Docker image builds
- Versioned container publishing
- AWS cloud deployment

---

# Architecture

The deployed WildTrace architecture currently consists of four containerized services running on an AWS EC2 instance.

```text
                         Internet
                            │
                            ▼
                       AWS EC2
                            │
                      Docker Engine
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
       FastAPI          PostgreSQL         Redis
           │                                 │
           │                                 ▼
           └──────────────────────────► Celery Worker
```

The FastAPI application handles HTTP requests and communicates with PostgreSQL through SQLAlchemy.

When a sighting is created:

1. FastAPI validates the incoming request.
2. SQLAlchemy persists the sighting to PostgreSQL.
3. The database transaction is committed.
4. FastAPI sends a background task to Redis.
5. The Celery worker consumes and processes the task.

The API and Celery worker use the same WildTrace Docker image but run as separate containers with different commands and responsibilities.

---

# Sighting Model

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

---

# API Endpoints

## Health

```http
GET /healthz
```

Checks whether the FastAPI application is running.

Example response:

```json
{
  "status": "ok"
}
```

## Readiness

```http
GET /readyz
```

Checks whether the application is ready and can communicate with PostgreSQL.

Example response:

```json
{
  "status": "ready"
}
```

---

## Create a Sighting

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

Creating a sighting also queues a background processing task through Redis and Celery.

---

## Retrieve Sightings

```http
GET /api/v1/sightings
```

### Pagination

```http
GET /api/v1/sightings?skip=0&limit=20
```

### Species filtering

```http
GET /api/v1/sightings?species=seal
```

### Observation date filtering

```http
GET /api/v1/sightings?observed_from=2026-10-01T00:00:00Z&observed_to=2026-10-31T23:59:59Z
```

Filtering and pagination parameters can be combined.

---

## Retrieve a Sighting

```http
GET /api/v1/sightings/{sighting_id}
```

Requests for nonexistent sightings return:

```text
404 Not Found
```

---

## Update a Sighting

```http
PATCH /api/v1/sightings/{sighting_id}
```

PATCH supports partial updates, allowing individual fields to be modified without replacing the entire sighting.

---

## Delete a Sighting

```http
DELETE /api/v1/sightings/{sighting_id}
```

Successful deletion returns:

```text
204 No Content
```

---

# Local Development

## Requirements

Install:

- Docker
- Docker Compose

Clone the repository:

```bash
git clone <repository-url>
cd wildtrace
```

Build and start the local environment:

```bash
docker compose up --build -d
```

The local Docker Compose environment includes:

```text
api
db
test-db
redis
worker
```

Check the services:

```bash
docker compose ps
```

The API is available locally at:

```text
http://localhost:8000
```

Interactive FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# Background Processing

WildTrace uses Redis and Celery for asynchronous background processing.

```text
POST /api/v1/sightings
          │
          ▼
       FastAPI
          │
          ▼
      PostgreSQL
          │
       commit
          │
          ▼
        Redis
          │
          ▼
    Celery Worker
```

The sighting is committed to PostgreSQL before the background task is queued. This prevents the worker from receiving an ID for a database record that has not yet been committed.

During automated API tests, Celery task dispatch is mocked. This keeps the API test suite independent of Redis and Celery while still verifying that the expected background task is dispatched.

---

# Database Migrations

WildTrace uses Alembic for database schema management.

The application does not rely on automatic table creation during startup.

Apply all migrations:

```bash
docker compose exec api alembic upgrade head
```

Check the current migration:

```bash
docker compose exec api alembic current
```

Create a migration after modifying the SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
```

Migration files are stored in:

```text
alembic/versions/
```

The initial sightings migration is:

```text
e933e80caa48
```

Database migrations are also executed during continuous integration.

---

# Testing

WildTrace includes automated tests covering the API and its main behavior.

Current test coverage includes:

- Sighting creation
- Sighting retrieval
- Updates
- Deletion
- Request validation
- Species filtering
- Observation date filtering
- Health endpoint behavior
- Celery task dispatch

Run the tests:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest -v --cov=app --cov-report=term-missing
```

The CI pipeline requires a minimum of:

```text
85% coverage
```

---

# Code Quality

WildTrace uses Ruff for automated Python linting.

Run it locally:

```bash
ruff check .
```

Ruff is also executed automatically by GitHub Actions.

---

# Security

WildTrace performs security checks at both the Python dependency and container image levels.

## Dependency Scanning

Python dependencies are checked for known vulnerabilities using:

```bash
pip-audit -r requirements.txt
```

## Container Scanning

The final Docker image is scanned using **Trivy**.

Trivy checks components contained in the final image, including operating-system packages and application dependencies, for known vulnerabilities.

The CI pipeline is configured to fail when qualifying critical vulnerabilities are detected.

This means the container image is security-scanned before being published for deployment.

---

# Docker

WildTrace uses a multi-stage Docker build.

The build stage creates the Python virtual environment and installs application dependencies.

The final stage contains only the runtime components needed to execute WildTrace.

The resulting image runs the application as a non-root user.

The same application image can run different workloads.

For example:

```text
WildTrace image
      │
      ├── FastAPI container
      │
      └── Celery worker container
```

The API runs:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

while the worker runs:

```text
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

---

# Continuous Integration

WildTrace uses GitHub Actions for continuous integration.

The pipeline validates application changes before a container image is published.

```text
Git Push / Pull Request
          │
          ▼
     GitHub Actions
          │
          ├── Install dependencies
          ├── Run Alembic migrations
          ├── Ruff
          ├── pip-audit
          ├── Pytest
          └── Coverage enforcement
          │
          ▼
      Docker Build
          │
          ▼
       Trivy Scan
          │
          ▼
    Validated Image
```

A failed migration, linting check, dependency audit, test, coverage check, Docker build, or qualifying security scan prevents the pipeline from completing successfully.

---

# Container Registry

Validated WildTrace images are published to **GitHub Container Registry (GHCR)**.

The EC2 server therefore does not need to clone the repository and rebuild the application.

Instead:

```text
Source Code
     │
     ▼
GitHub Actions
     │
     ├── Test
     ├── Validate
     ├── Build
     └── Scan
     │
     ▼
GHCR
     │
     ▼
AWS EC2
```

Each successful build is tagged with:

```text
latest
<git-commit-sha>
```

For example:

```text
ghcr.io/<owner>/<repository>:latest
ghcr.io/<owner>/<repository>:<commit-sha>
```

The `latest` tag identifies the most recently published image.

The commit-SHA tag provides traceability between the deployed container image and the exact Git revision used to build it.

This also provides the foundation for deployment rollback to a previously validated image.

---

# AWS Deployment

WildTrace is currently deployed to an **Ubuntu 24.04 LTS EC2 instance**.

Current EC2 environment:

```text
Operating System: Ubuntu 24.04 LTS
Architecture:     x86_64
Instance type:    t3.micro
Compute:          2 vCPU
Memory:           ~1 GiB
Storage:          20 GiB gp3 EBS
Swap:             1 GiB
Container runtime: Docker Engine
Orchestration:    Docker Compose
```

The deployment uses the Docker image published by the GitHub Actions pipeline to GHCR.

---

## Production Compose Architecture

The EC2 deployment contains:

```text
Docker Compose
│
├── api
│   └── GHCR WildTrace image
│
├── worker
│   └── GHCR WildTrace image
│
├── db
│   └── PostgreSQL 16 Alpine
│
└── redis
    └── Redis 7 Alpine
```

Unlike the development environment, the deployment configuration:

- does not build the application from source
- does not mount application source directories
- does not run the test database
- pulls the validated WildTrace image from GHCR
- persists PostgreSQL data using a Docker volume
- uses restart policies for long-running services

---

## Deployment Configuration

The production deployment uses a separate Compose configuration:

```text
compose.prod.yml
```

Application configuration and database credentials are provided through environment variables rather than being embedded directly into the Compose configuration.

The production environment file is protected with restricted filesystem permissions and is not stored in the application repository.

---

## AWS Networking

The EC2 instance runs inside an AWS VPC and uses an AWS Security Group as its network firewall.

SSH access is restricted rather than exposing port `22` universally.

PostgreSQL and Redis are not published directly to the host or the public Internet.

```text
Internet
   │
   ▼
AWS Security Group
   │
   ▼
EC2
   │
   ├── FastAPI
   │
   ├── PostgreSQL ── internal only
   │
   ├── Redis ─────── internal only
   │
   └── Celery
```

This prevents direct Internet access to the PostgreSQL and Redis services.

---

## Deployment Migrations

Before starting the complete application stack, database migrations are applied using the application image:

```bash
docker compose -f compose.prod.yml run --rm api alembic upgrade head
```

The deployed database currently reports:

```text
e933e80caa48 (head)
```

This confirms that the deployed PostgreSQL schema is managed through the same Alembic migration history as the application source.

---

## Deployment Health Checks

The deployed application exposes separate liveness and readiness endpoints.

Application health:

```bash
curl http://localhost:8000/healthz
```

Response:

```json
{
  "status": "ok"
}
```

Database readiness:

```bash
curl http://localhost:8000/readyz
```

Response:

```json
{
  "status": "ready"
}
```

PostgreSQL also uses a Docker health check before dependent application services are started.

---

## Deployment Resource Usage

The complete application currently runs on a small `t3.micro` instance.

The four application services have demonstrated low idle memory usage, with the API and Celery worker being the largest application containers.

Because the instance provides approximately 1 GiB of RAM, a 1 GiB swap file is configured as additional protection against temporary memory pressure.

The deployment currently demonstrates that the complete WildTrace stack can operate within a small cloud environment while resource usage remains observable through Linux and Docker tooling.

---

# Current Delivery Pipeline

WildTrace currently implements the following delivery path:

```text
Developer
    │
    │ git push
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Alembic migrations
    ├── Ruff
    ├── pip-audit
    ├── Pytest
    └── Coverage
    │
    ▼
Docker Build
    │
    ▼
Trivy Scan
    │
    ▼
GHCR
    │
    ├── :latest
    └── :<commit-sha>
    │
    │ docker pull
    ▼
AWS EC2
    │
    ▼
Docker Compose
    │
    ├── FastAPI
    ├── Celery
    ├── PostgreSQL
    └── Redis
```

At the current stage, CI and container publishing are automated.

The AWS deployment itself is currently performed manually from the validated GHCR artifact.

Automating this final deployment step will turn the existing pipeline into a complete CI/CD workflow.

---

# Project Structure

```text
wildtrace/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── alembic/
│   ├── versions/
│   │   └── e933e80caa48_create_sightings_table.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── routers/
│   │   └── sightings.py
│   │
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── tests/
│   ├── conftest.py
│   └── test_sightings.py
│
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

# Development Status

## Implemented

### Backend

- REST API
- CRUD operations
- Filtering
- Pagination
- Pydantic validation
- PostgreSQL persistence
- SQLAlchemy ORM
- Health and readiness endpoints

### Database

- PostgreSQL 16
- Alembic migrations
- Persistent deployment volume
- Database health checks

### Background Processing

- Redis broker
- Celery worker
- Asynchronous task dispatch
- Celery mocking during API tests

### Testing & Quality

- Pytest
- Automated API tests
- Coverage enforcement
- Ruff linting

### Security

- pip-audit
- Trivy container scanning
- Non-root application container
- Restricted EC2 SSH access
- PostgreSQL not publicly exposed
- Redis not publicly exposed
- Deployment credentials separated from Compose configuration

### Containers

- Multi-stage Dockerfile
- Docker Compose development environment
- Separate deployment Compose configuration
- GHCR image publishing
- `latest` image tagging
- Git commit SHA image tagging

### AWS

- Ubuntu EC2 deployment
- EBS storage
- AWS VPC networking
- Security Group configuration
- Docker installation
- Docker Compose deployment
- Persistent PostgreSQL storage
- Deployment migrations
- Application health verification

---

# DevOps Roadmap

## 1. Public API Access

Expose the API through controlled network rules and verify the deployed API externally.

## 2. Reverse Proxy and HTTPS

Introduce a reverse proxy and TLS so the API can be accessed through standard HTTP/HTTPS ports instead of exposing the application server directly.

## 3. Continuous Deployment

Extend GitHub Actions so successful builds can automatically deploy validated GHCR images to AWS.

The target pipeline is:

```text
Push
  ↓
Test
  ↓
Scan
  ↓
Build
  ↓
Publish
  ↓
Deploy
  ↓
Health Check
```

## 4. Deployment Versioning and Rollback

Deploy immutable commit-SHA image versions rather than depending solely on `latest`.

This will allow a deployment to be traced to an exact Git commit and enable rollback to previously validated images.

## 5. Infrastructure as Code

Introduce **Terraform** to provision and manage AWS infrastructure declaratively.

Potential resources include:

- EC2
- Security Groups
- networking
- storage
- IAM configuration

## 6. Kubernetes

Move the containerized services toward Kubernetes workloads and learn:

- Pods
- Deployments
- Services
- ConfigMaps
- Secrets
- health probes
- persistent storage
- rolling deployments

## 7. Observability

Add monitoring and metrics using:

- Prometheus
- Grafana

Potential metrics include:

- API request rate
- response latency
- HTTP errors
- CPU utilization
- memory utilization
- container health
- Celery task activity
- PostgreSQL availability

---

# Purpose

WildTrace is designed to demonstrate more than CRUD API development.

The project follows the evolution of an application through multiple software delivery stages:

```text
Application Development
          ↓
Automated Testing
          ↓
Database Migrations
          ↓
Containerization
          ↓
Security Scanning
          ↓
Continuous Integration
          ↓
Artifact Versioning
          ↓
Container Registry
          ↓
Cloud Deployment
          ↓
Continuous Deployment
          ↓
Infrastructure as Code
          ↓
Container Orchestration
          ↓
Observability
```

The current implementation demonstrates a working backend application with PostgreSQL persistence, asynchronous processing, automated testing, security validation, versioned Docker artifacts, and an operational AWS deployment.

The next phase focuses on safely exposing the API, automating deployments, improving deployment versioning and rollback, and moving infrastructure management toward Terraform and Kubernetes.