# Multi-tenant SaaS Backend

A production-style **Multi-tenant SaaS Backend** built with **Django REST Framework**. The project demonstrates workspace isolation, role-based access control (RBAC), asynchronous task notifications, Redis caching, Celery background processing, and Dockerized deployment.

This project was built to showcase backend engineering best practices including scalable API design, multi-tenancy, background jobs, database optimization, and clean architecture.

---

## Features

### Authentication
- JWT Authentication (Access & Refresh Tokens)
- Custom User Model
- Secure API Authentication

### Multi-Tenant Architecture
- Workspace-based tenant isolation
- Workspace context using `X-Workspace-ID`
- Data isolation between tenants

### Role Based Access Control (RBAC)
- Owner
- Admin
- Member

Permission-based access across all APIs.

### Workspace Management
- Create Workspace
- Update Workspace
- Archive Workspace
- Restore Workspace
- List User Workspaces

### Project Management
- Create Project
- Update Project
- Archive Project
- Restore Project
- List Workspace Projects

### Task Management
- Create Tasks
- Update Tasks
- Delete (Soft Delete)
- Restore Tasks
- Task Assignment
- Task Status Management

### Task Comments
- Add Comments
- List Comments

### File Attachments
- Upload Attachments
- Download Attachments

### Activity Logs
Tracks important business events including:

- Workspace creation
- Workspace updates
- Project creation
- Task updates
- Member management
- Archive/Restore actions

### Redis Caching
Caches:

- Workspace lookups
- Membership lookups

to reduce database queries during authorization.

### Asynchronous Email Notifications
Task assignment emails are sent asynchronously using:

- Celery
- Redis
- Brevo SMTP

> Note: Celery worker execution is available in the local Docker environment. Production requires a separate Celery Worker service.

Emails are triggered when:

- A task is created with an assignee
- A task is reassigned to another user

### Soft Delete
Implements soft deletion for business entities with restore functionality.

### Docker Support
Dockerized development environment including:

- Django
- PostgreSQL
- Redis
- Celery Worker

---

# Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.12 |
| Framework | Django |
| API | Django REST Framework |
| Authentication | Simple JWT |
| Database | PostgreSQL |
| Cache | Redis |
| Background Tasks | Celery |
| Email | Brevo SMTP |
| Containerization | Docker & Docker Compose |
| API Documentation | drf-spectacular (Swagger/OpenAPI) |

---

# Project Architecture

The application follows a scalable backend architecture using Django REST Framework, PostgreSQL, Redis, Celery, and SMTP email processing.

```
                         Client
                            │
                            ▼
                 Django REST Framework
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   PostgreSQL             Redis            Celery Worker
        │                   │                   │
        │                   │                   ▼
        │                   │              Brevo SMTP
        │                   │                   │
        │                   │                   ▼
        │                   │          Email Notification
        │                   │
        └───────────────────┴───────────────────┘
```

## Components

### Django REST Framework
- Handles API requests
- Authentication and authorization
- Workspace isolation
- Business logic

### PostgreSQL
- Stores application data
- User accounts
- Workspaces
- Projects
- Tasks
- Activity logs

### Redis
Used for:
- Workspace caching
- Membership caching
- Celery message broker

### Celery Worker
Handles asynchronous tasks:
- Task assignment emails
- Background processing

### Brevo SMTP
Used for:
- Sending email notifications

---

# Deployment Architecture

## Local Development

Docker Compose runs the complete architecture:

```
Django
  │
  ├── PostgreSQL Container
  │
  ├── Redis Container
  │
  └── Celery Worker Container
          │
          └── Brevo SMTP
```

---

## Production Deployment

The hosted demo uses:

```
                         Client
                            │
                            ▼
                   Render Web Service
                    (Django API)
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
    Neon PostgreSQL                      Upstash Redis
```

Celery remains part of the application architecture:

```
                         Celery Worker
                              │
                              ▼
                         Upstash Redis
                              │
                              ▼
                         Brevo SMTP
```

The current Render free-tier deployment does not include a separate Background Worker service, so the Celery Worker is not running in the hosted demo.

To enable production background processing, deploy Celery as a separate worker service.

---

# Folder Structure

```
Multi-tenant Django APP/

├── apps/
│   ├── accounts/
│   ├── workspaces/
│   ├── projects/
│   ├── notifications/
│   └── audit/
│
├── common/
│
├── config/
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── manage.py
└── requirements.txt
```

---

# API Documentation

Swagger UI

```
/api/v1/docs/
```

OpenAPI Schema

```
/api/v1/schema/
```

Redoc

```
/api/v1/redoc/
```

---

# Local Setup

Clone the repository

```bash
https://github.com/CodeBySarvesh/multitenant-saas-platform.git

cd Multi-tenant Django APP
```

Create environment variables

```bash
cp .env.example .env
```

Build containers

```bash
docker compose up --build
```

Run migrations

```bash
docker compose exec web python manage.py migrate
```

Create superuser

```bash
docker compose exec web python manage.py createsuperuser
```

Access

```
http://localhost:8000
```

Swagger

```
http://localhost:8000/api/docs/
```

---

# Running Celery

Worker

```bash
docker compose up celery
```

or

```bash
docker compose exec celery celery -A config worker -l info
```

---

# Background Tasks Deployment Note

## Local Development

The local Docker environment runs:

- Django web service
- PostgreSQL database
- Redis server
- Celery worker

Redis acts as the message broker, and Celery processes background jobs such as task assignment email notifications.

Start the complete development environment:

```bash
docker compose up

# Production Deployment (Render)

The hosted demo is deployed on Render.

Production services:

- Django REST API runs as a Render Web Service.
- PostgreSQL is hosted on Neon Database.
- Redis is hosted on Upstash Redis.

The Render free tier does not include Background Worker services, therefore the Celery worker is not deployed in the hosted demo.

As a result:
- API functionality works normally.
- Redis caching works normally.
- Celery background tasks (such as task assignment emails) require a separate Celery Worker deployment.

For a full production setup with asynchronous processing, deploy Celery as a separate background worker service.

---

# Environment Variables

Create a `.env` file using `.env.example`.

Required variables include:

```
DEBUG=

SECRET_KEY=

ALLOWED_HOSTS=

DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=

REDIS_URL=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

FRONTEND_URL=
```

---

# Multi-Tenant Request Header

Every authenticated request must include:

```
X-Workspace-ID
```

Example

```
X-Workspace-ID: 1
```

This identifies the active tenant and ensures complete workspace isolation.

---

# Security

- JWT Authentication
- Role Based Access Control
- Workspace Isolation
- Environment Variable Configuration
- Soft Delete Protection

---

# Performance Optimizations

- Redis caching
- Optimized ORM queries using `select_related()`
- Background task processing with Celery
- Non-blocking email notifications

---

# Email Notifications

Task assignment notifications are processed asynchronously.

Workflow

```
Create Task
        │
        ▼
Save Database
        │
        ▼
Celery Queue
        │
        ▼
Redis Broker
        │
        ▼
Celery Worker
        │
        ▼
Brevo SMTP
        │
        ▼
Recipient
```

---

# Future Improvements

- Unit & Integration Tests
- CI/CD Pipeline
- Object Storage (AWS S3)
- WebSocket Notifications
- Rate Limiting
- Audit Dashboard

---

# License

This project is licensed under the MIT License.

---

# Author

**Sarvesh Pawar**

Backend Engineer

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker
- AWS
