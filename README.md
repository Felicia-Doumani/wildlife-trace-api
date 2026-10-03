# WildTrace API

WildTrace is a containerized REST API for recording, managing, and retrieving wildlife sightings.

The project is built as a backend and DevOps portfolio project demonstrating the path from application development to automated testing, containerization, security scanning, container publishing, cloud deployment, and infrastructure management.

WildTrace is currently deployed on **AWS EC2**. The deployed environment runs FastAPI, PostgreSQL, Redis, and Celery as Docker containers, with **Nginx acting as the public reverse proxy**.

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
- AWS VPC
- AWS Security Groups
- AWS IAM
- AWS Systems Manager (SSM)
- Nginx

---

# Features

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
- Nginx reverse proxy
- Restricted application-port exposure
- AWS Systems Manager access

---

# Architecture

The deployed WildTrace architecture currently consists of four application containers running on an AWS EC2 instance behind an Nginx reverse proxy.

```text
                         Internet
                            │
                            ▼
                   AWS Security Group
                            │
                         TCP :80
                            │
                            ▼
                         Nginx
                            │
                            │ localhost
                            ▼
                    127.0.0.1:8000
                            │
                            ▼
                         FastAPI
                         /     \
                        /       \
                       ▼         ▼
                 PostgreSQL    Redis
                                  │
                                  ▼
                            Celery Worker
```

Nginx is the public entry point to the application.

FastAPI itself is not directly exposed to the Internet. Docker binds the API to:

```text
127.0.0.1:8000
```

which means only processes running on the EC2 host, such as Nginx, can access the application port directly.

PostgreSQL and Redis do not publish host ports and remain accessible only through the internal Docker network.

---

# Request Flow

A normal API request follows:

```text
Client
  │
  ▼
Internet
  │
  ▼
AWS Security Group
  │
  ▼
Nginx :80
  │
  ▼
FastAPI :8000
  │
  ▼
SQLAlchemy
  │
  ▼
PostgreSQL
```

When a sighting is created:

1. Nginx receives the public HTTP request.
2. Nginx forwards it to FastAPI on `127.0.0.1:8000`.
3. FastAPI validates the request using Pydantic.
4. SQLAlchemy persists the sighting to PostgreSQL.
5. The database transaction is committed.
6. FastAPI sends a background task to Redis.
7. The Celery worker receives and processes the task.

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

---

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

Example:

```json
{
  "species": "Mediterranean monk seal",
  "latitude": 37.75,
  "longitude": 26.98,
  "observed_at": "2026-10-03T12:00:00Z",
  "photo_url": null,
  "notes": "Observed near the coastline."
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

Build and start the development environment:

```bash
docker compose up --build -d
```

The local environment contains:

```text
api
db
test-db
redis
worker
```

Check the containers:

```bash
docker compose ps
```

The development API is available at:

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

During automated API tests, Celery task dispatch is mocked. This keeps the API test suite independent of Redis and Celery while still verifying that the expected task is dispatched.

---

# Database Migrations

WildTrace uses Alembic for database schema management.

The application does not rely on automatic table creation during startup.

Apply migrations locally:

```bash
docker compose exec api alembic upgrade head
```

Check the current migration:

```bash
docker compose exec api alembic current
```

Create a new migration:

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

Database migrations are also validated during continuous integration.

---

# Testing

WildTrace includes automated tests covering the API and its main behavior.

Current coverage includes:

- Sighting creation
- Sighting retrieval
- Updates
- Deletion
- Request validation
- Species filtering
- Observation date filtering
- Health endpoint behavior
- Celery task dispatch

Run tests:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest -v --cov=app --cov-report=term-missing
```

The CI pipeline enforces a minimum of:

```text
85% coverage
```

---

# Code Quality

WildTrace uses Ruff for automated Python linting.

Run locally:

```bash
ruff check .
```

Ruff is also executed automatically by GitHub Actions.

---

# Security

WildTrace performs security checks at both the dependency and container-image levels.

## Dependency Scanning

Python dependencies are checked for known vulnerabilities using:

```bash
pip-audit -r requirements.txt
```

## Container Scanning

The final Docker image is scanned using **Trivy**.

Trivy checks the components contained in the final image, including operating-system packages and application dependencies, for known vulnerabilities.

The CI pipeline is configured to fail when qualifying critical vulnerabilities are detected.

The container is therefore security-scanned before being published for deployment.

---

# Docker

WildTrace uses a multi-stage Docker build.

The build stage creates the Python virtual environment and installs application dependencies.

The final stage contains the runtime components required to execute WildTrace.

The resulting image runs the application as a non-root user.

The same application image runs different workloads:

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

The Celery worker runs:

```text
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

For the small production EC2 environment, worker concurrency can be limited to reduce memory consumption.

---

# Continuous Integration

WildTrace uses GitHub Actions for continuous integration.

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
     Publish to GHCR
```

A failed migration, linting check, dependency audit, test, coverage check, Docker build, or qualifying security scan prevents the pipeline from completing successfully.

---

# Container Registry

Validated WildTrace images are published to **GitHub Container Registry (GHCR)**.

The EC2 server therefore does not need to clone and compile the application source for deployment.

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

Successful builds are tagged with:

```text
latest
<git-commit-sha>
```

For example:

```text
ghcr.io/<owner>/<repository>:latest
ghcr.io/<owner>/<repository>:<commit-sha>
```

The commit-SHA tag provides traceability between a Docker artifact and the exact Git revision used to build it.

This provides the foundation for immutable deployments and rollback.

---

# AWS Deployment

WildTrace is currently deployed on an **Ubuntu 24.04 LTS EC2 instance**.

Current environment:

```text
Operating System:  Ubuntu 24.04 LTS
Architecture:      x86_64
Instance type:     t3.micro
Compute:           2 vCPU
Memory:            ~1 GiB
Storage:           20 GiB gp3 EBS
Swap:              1 GiB
Container runtime: Docker Engine
Orchestration:     Docker Compose
Reverse proxy:     Nginx
```

The deployment uses Docker images produced by the GitHub Actions pipeline and published to GHCR.

The application source is developed locally rather than directly on the EC2 server.

---

# Production Docker Compose

Production deployment configuration is stored separately in:

```text
compose.prod.yml
```

Unlike the development environment, production:

- does not build the application from source
- does not mount application source directories
- does not run the test database
- pulls validated application images from GHCR
- persists PostgreSQL data using a Docker volume
- uses restart policies
- keeps PostgreSQL internal
- keeps Redis internal
- binds FastAPI only to EC2 localhost

The production configuration is version-controlled in the Git repository.

Secrets are not stored in `compose.prod.yml`.

---

# Deployment Configuration

Database credentials are supplied through environment variables.

The real production `.env` file exists on the EC2 server and is not committed to Git.

Example variables:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

The application image supports a configurable image tag:

```text
${IMAGE_TAG:-latest}
```

This allows the same Compose configuration to run either the latest image or an exact Git commit image.

For example:

```bash
IMAGE_TAG=<commit-sha> docker compose -f compose.prod.yml up -d
```

This forms the basis for immutable, traceable deployments.

---

# Production Networking

WildTrace uses multiple layers of network isolation.

## AWS Security Group

The EC2 Security Group acts as the cloud-level firewall.

Public HTTP traffic is accepted on:

```text
TCP 80
```

SSH access is restricted rather than universally exposed.

PostgreSQL and Redis are not exposed publicly.

---

## Nginx Reverse Proxy

Nginx runs directly on the EC2 host and acts as the public application entry point.

```text
Internet
   │
   ▼
TCP :80
   │
   ▼
Nginx
   │
   ▼
127.0.0.1:8000
   │
   ▼
FastAPI
```

A request such as:

```text
http://<server>/healthz
```

is received by Nginx and forwarded internally to FastAPI.

---

## FastAPI Port Isolation

Docker binds the FastAPI container using:

```text
127.0.0.1:8000:8000
```

rather than:

```text
0.0.0.0:8000:8000
```

Therefore port `8000` is not directly reachable through the EC2 network interface.

This provides an additional layer of protection beyond the AWS Security Group.

---

## Internal Services

PostgreSQL and Redis have no published host ports.

```text
Internet
   │
   ▼
AWS Security Group
   │
   ▼
Nginx :80
   │
   ▼
FastAPI
   │
   ├──────────────► PostgreSQL
   │
   └──► Redis
          │
          ▼
     Celery Worker
```

PostgreSQL and Redis communicate with application containers over the Docker network.

---

# Deployment Migrations

Before starting a new application version, Alembic migrations can be executed using the application image:

```bash
docker compose -f compose.prod.yml run --rm api alembic upgrade head
```

The deployed database currently uses the migration:

```text
e933e80caa48 (head)
```

This confirms that the production database schema is controlled by the same migration history stored in Git.

---

# Deployment Verification

The deployed application has been tested externally.

Public health request:

```bash
curl http://<server>/healthz
```

Response:

```json
{
  "status": "ok"
}
```

The readiness endpoint confirms database connectivity:

```bash
curl http://<server>/readyz
```

Response:

```json
{
  "status": "ready"
}
```

A real sighting has also been successfully submitted through the public API.

The request:

1. reached Nginx
2. was forwarded to FastAPI
3. passed Pydantic validation
4. was persisted to PostgreSQL
5. generated a Redis-backed Celery task
6. was received by the Celery worker
7. completed successfully

This verifies the complete deployed application path.

---

# Resource Management

WildTrace currently runs on a small `t3.micro` instance with approximately 1 GiB RAM.

A 1 GiB swap file is configured as protection against temporary memory pressure.

The deployed services have demonstrated low idle container memory usage, with FastAPI and Celery being the largest application containers.

Resource usage can be inspected with:

```bash
free -h
```

and:

```bash
docker stats --no-stream
```

The small deployment environment makes resource consumption an explicit part of the infrastructure design.

---

# AWS Systems Manager

The EC2 instance is registered with **AWS Systems Manager (SSM)**.

The SSM Agent runs on the EC2 instance and communicates with AWS Systems Manager.

The instance has a dedicated IAM role with the permissions required to operate as an SSM managed node.

This provides an alternative administrative path to traditional SSH:

```text
Traditional access

Developer
    │
    │ SSH + private key
    ▼
EC2 :22
```

versus:

```text
SSM access

AWS-authenticated user
        │
        ▼
AWS Systems Manager
        │
        ▼
SSM Agent
        │
        ▼
EC2
```

A Session Manager connection has been successfully established to the WildTrace EC2 instance.

Session Manager provides browser-based shell access without requiring the user to directly authenticate to the server using the EC2 SSH private key.

This infrastructure will also provide the foundation for executing deployment commands through AWS rather than exposing SSH access to GitHub-hosted CI runners.

---

# IAM

WildTrace currently uses an EC2 IAM role for Systems Manager integration.

The role allows the EC2 instance to authenticate to AWS Systems Manager and operate as a managed node.

The important distinction is:

```text
IAM Role
   │
   └── defines what an AWS identity/resource is allowed to do

SSM
   │
   └── provides remote management of the EC2 instance
```

The next deployment phase will introduce a separate, narrowly scoped identity for GitHub Actions.

---

# Current Delivery Pipeline

The current automated path is:

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
    ├── Alembic validation
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
```

Deployment currently continues manually:

```text
GHCR
  │
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

Therefore:

```text
CI                 ✅ Automated
Image publishing   ✅ Automated
Cloud deployment   ✅ Implemented
CD                 🚧 In progress
```

The project should not yet be described as having completed Continuous Deployment.

---

# Planned Continuous Deployment Architecture

The next stage is to allow GitHub Actions to securely request deployments through AWS.

The planned architecture is:

```text
git push main
      │
      ▼
GitHub Actions
      │
      ├── Test
      ├── Lint
      ├── Audit
      ├── Build
      └── Scan
      │
      ▼
GHCR
      │
      │ commit-SHA image
      ▼
GitHub → AWS Authentication
      │
      ▼
AWS Systems Manager
      │
      ▼
EC2
      │
      ├── Pull exact image
      ├── Run Alembic migrations
      ├── Recreate application containers
      └── Run health check
```

The intended authentication mechanism is **GitHub OIDC with AWS IAM**.

This allows GitHub Actions to obtain temporary AWS credentials instead of storing permanent AWS access keys in GitHub.

The OIDC/CD configuration is not yet complete.

---

# Development vs Deployment

Application development is performed on the developer workstation.

```text
LOCAL COMPUTER
────────────────────
Python development
FastAPI changes
Tests
Alembic migrations
Docker configuration
Infrastructure configuration
        │
        │ git push
        ▼
```

GitHub acts as the source-code and CI platform:

```text
GITHUB
────────────────────
Repository
GitHub Actions
Testing
Security validation
Container building
        │
        ▼
GHCR
```

AWS is the runtime environment:

```text
AWS EC2
────────────────────
Nginx
Docker Engine
FastAPI
PostgreSQL
Redis
Celery
SSM Agent
```

Normal application development is **not performed directly on the EC2 server**.

The goal of Continuous Deployment is to further reduce the need for manual server administration during normal releases.

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
├── compose.prod.yml
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
- Persistent production volume
- Database health checks

### Background Processing

- Redis broker
- Celery worker
- Asynchronous task dispatch
- Celery mocking during API tests

### Testing & Quality

- Pytest
- Automated API tests
- 85% minimum coverage enforcement
- Ruff linting

### Security

- pip-audit
- Trivy container scanning
- Non-root application container
- Restricted SSH access
- PostgreSQL not publicly exposed
- Redis not publicly exposed
- FastAPI port not publicly exposed
- Nginx as public application boundary
- Deployment credentials separated from Compose configuration

### Containers

- Multi-stage Dockerfile
- Docker Compose development environment
- Separate production Compose configuration
- Version-controlled production configuration
- GHCR image publishing
- `latest` image tagging
- Git commit SHA image tagging
- Configurable production `IMAGE_TAG`

### AWS

- Ubuntu EC2 deployment
- EBS storage
- AWS VPC networking
- Security Group configuration
- Docker Engine
- Docker Compose deployment
- Persistent PostgreSQL storage
- Deployment migrations
- Public application verification
- Nginx reverse proxy
- IAM instance role
- SSM Agent registration
- Systems Manager Session Manager access

### CI

- GitHub Actions
- Automated tests
- Automated migrations
- Automated linting
- Dependency auditing
- Container build
- Container security scanning
- GHCR publishing

---

# DevOps Roadmap

## 1. Continuous Deployment

Complete automated deployment from GitHub Actions to AWS.

Planned flow:

```text
Push to main
      ↓
CI
      ↓
Build
      ↓
Security Scan
      ↓
GHCR
      ↓
AWS Authentication
      ↓
SSM Deployment
      ↓
Alembic Migration
      ↓
Container Update
      ↓
Health Check
```

---

## 2. GitHub OIDC + AWS IAM

Configure GitHub Actions to authenticate to AWS using OpenID Connect.

The goal is to use short-lived credentials rather than storing permanent AWS access keys.

The deployment IAM role should follow least-privilege principles.

---

## 3. Immutable Deployment and Rollback

Deploy exact commit-SHA image versions rather than relying solely on `latest`.

For example:

```text
ghcr.io/<owner>/<repository>:<commit-sha>
```

This will make each deployment traceable to an exact Git commit and provide a clean rollback mechanism.

---

## 4. HTTPS

The current deployment uses HTTP through Nginx.

HTTPS is intentionally deferred until a domain or suitable DNS name is available.

Future architecture:

```text
Internet
   │
   ▼
HTTPS :443
   │
   ▼
Nginx + TLS
   │
   ▼
FastAPI
```

---

## 5. Infrastructure as Code

Introduce **Terraform** to provision AWS infrastructure declaratively.

Potential resources include:

- EC2
- Security Groups
- networking
- IAM roles
- storage
- Systems Manager-related configuration

---

## 6. Kubernetes

Move the containerized application toward Kubernetes workloads and learn:

- Pods
- Deployments
- Services
- ConfigMaps
- Secrets
- health probes
- persistent storage
- rolling deployments

---

## 7. Observability

Introduce monitoring and metrics using:

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
Reverse Proxy / Network Hardening
          ↓
Secure Cloud Administration
          ↓
Continuous Deployment
          ↓
Infrastructure as Code
          ↓
Container Orchestration
          ↓
Observability
```

The current implementation demonstrates a working backend application with PostgreSQL persistence, asynchronous Redis/Celery processing, automated testing, database migrations, security validation, versioned Docker artifacts, GHCR publishing, an operational AWS EC2 deployment, Nginx reverse proxying, network isolation, IAM-based EC2 permissions, and AWS Systems Manager access.

The next phase focuses on completing Continuous Deployment using GitHub Actions, AWS IAM, GitHub OIDC, and Systems Manager, followed by immutable deployments and rollback support.