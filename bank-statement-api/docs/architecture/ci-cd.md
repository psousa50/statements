# Architecture and Deployment Plan

This document outlines the overall architecture, environment setup, and deployment strategy for a full-stack application composed of:

- A **FastAPI** backend (Python)
- A **React + Vite** frontend
- A **Celery** worker and beat process for background and scheduled tasks
- **PostgreSQL** for data persistence
- **Redis** (Upstash) as the Celery message broker
- CI/CD managed via **GitHub Actions**
- Hosting and orchestration provided by **Render**, using a single workspace

---

## 1. Application Components

### Backend
- Implemented using **FastAPI**
- Database access via **SQLAlchemy**
- Migrations handled with **Alembic**
- Exposes a RESTful API
- Communicates with Redis and PostgreSQL
- Deployed as a web service on Render

### Frontend
- Implemented with **React** using **Vite** as the build tool
- Built as a static site
- Communicates with the backend via the API URL
- Deployed as a static site on Render

### Celery Worker
- Handles background jobs such as categorizing transactions
- Uses **Redis (Upstash)** as the broker
- Has access to the same PostgreSQL database as the backend
- Deployed as a **worker service** on Render

### Celery Beat
- Manages scheduled tasks (periodic jobs)
- Runs as a separate background service
- Shares the same environment and broker as the worker
- Also deployed as a **worker service** on Render

---

## 2. Environment Strategy

The project defines three primary environments:

| Environment | Purpose                    | Database                   | Redis                      |
|-------------|----------------------------|----------------------------|----------------------------|
| **Development** | Manual testing & validation | Neon (main branch)         | Upstash instance #1        |
| **Testing**     | CI-driven, ephemeral tests  | Neon (ephemeral branch)    | Upstash instance #2 (or shared, isolated via prefix) |
| **Production**  | Live deployment            | Render-managed Postgres DB | Upstash instance #3        |

### Environment Isolation
- Each environment has its own **PostgreSQL** instance
- Redis is isolated by creating separate Upstash instances per environment
- Environment variables are used to switch configurations cleanly

---

## 3. Database Management

### Production
- Hosted on **Render's managed PostgreSQL**
- Used exclusively by the production backend and worker

### Development
- Hosted on **Neon** using the main branch
- Accessible to both dev backend and local testing

### Test (CI)
- Each CI run creates an **ephemeral Neon branch** from a clean "template" DB
- This ensures full test isolation with no side effects
- CI jobs handle creation and teardown of these branches dynamically

---

## 4. Redis Setup

- Redis is hosted on **Upstash** (one instance per environment)
- Used by Celery for:
  - Task queuing
  - Scheduled tasks via Celery Beat
- Connection URL is passed as an environment variable (`REDIS_URL`)

---

## 5. CI/CD Workflow

- GitHub Actions is used for continuous integration and deployment
- The pipeline runs when changes are pushed to the `main` branch
- Steps:
  1. Deploy backend and frontend to **development**
  2. Run **Playwright end-to-end tests** against the dev environment using a **test database**
  3. If tests pass, deploy backend and frontend to **production**

This guarantees that only thoroughly tested code reaches production.

---

## 6. Render Deployment Overview

All services are deployed within a **single Render workspace**, including:

| Service        | Type      | Environment |
|----------------|-----------|-------------|
| Backend (dev)  | Web       | Development |
| Frontend (dev) | Static    | Development |
| Backend (prod) | Web       | Production  |
| Frontend (prod)| Static    | Production  |
| Celery Worker  | Worker    | All         |
| Celery Beat    | Worker    | All         |

This setup simplifies management, avoids workspace limits, and keeps CI/CD centralized.

---

## 7. Secrets and Configuration

- Environment-specific variables (e.g. `DATABASE_URL`, `REDIS_URL`, `ENV`) are injected:
  - via Render dashboard for dev/prod
  - via GitHub Actions secrets for test
- App uses a config layer to switch behavior based on the `ENV` variable (`development`, `test`, `production`)

---

## Next Steps

Once the architecture and deployment plan is approved, the following can be implemented:
- `render.yaml` to define all services and env vars
- GitHub Actions workflow for CI/CD, testing, and production deploy
- Scripts to manage Neon test branches
- `config.py` to manage env-specific settings in the backend