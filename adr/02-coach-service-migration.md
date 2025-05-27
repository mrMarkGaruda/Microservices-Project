**FitCo: AI Fitness Coach Application Documentation**

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Configuration](#installation--configuration)
4. [Application Architecture](#application-architecture)

   * [Directory Structure](#directory-structure)
   * [Flask Blueprints & Endpoints](#flask-blueprints--endpoints)
5. [Database Schema & Data Initialization](#database-schema--data-initialization)

   * [Muscle Groups](#muscle-groups)
   * [Exercises](#exercises)
   * [Exercise–Muscle Groups Mapping](#exercise–muscle-groups-mapping)
   * [Initialization Script](#initialization-script)
6. [Service Layer & Pydantic Models](#service-layer--pydantic-models)
7. [Testing](#testing)

   * [Unit & Integration Tests](#unit--integration-tests)
   * [Fixing the Failing Test](#fixing-the-failing-test)
8. [Containerization (Docker)](#containerization-docker)

   * [Dockerfile](#dockerfile)
   * [docker-compose](#docker-compose)
9. [Load Testing (k6)](#load-testing-k6)

   * [Writing & Running k6 Scripts](#writing--running-k6-scripts)
   * [Interpreting Results](#interpreting-results)
10. [Microservice: `coach`](#microservice-coach)

    * [Responsibility & Scope](#responsibility--scope)
    * [API Specification](#api-specification)
    * [Strangler Fig Migration](#strangler-fig-migration)
    * [ADR: Migration Design Document](#adr-migration-design-document)
11. [Environment Variables](#environment-variables)
12. [Deployment & CI/CD](#deployment--cicd)
13. [Contact & Delivery](#contact--delivery)

---

## 1. Project Overview

**FitCo** is a Flask‑based AI fitness coach platform that enables users to set goals, retrieve personalized Workout of the Day (WOD), track exercise history, manage nutrition guidance, and handle premium subscriptions.

Key features:

* Goal management: weight loss, muscle gain, endurance.
* WOD generation (AI‑powered).
* Dietary guidance endpoint.
* User profile, metrics, and preferences.
* Secure payment for premium plans.
* Persistent exercise history to avoid repeats.

Scope of this documentation: all modules, setup steps, DB schema, endpoints, tests, Dockerization, load testing, and the coach microservice migration.

---

## 2. Prerequisites

* **Python** ≥ 3.9
* **PostgreSQL** ≥ 12
* **Docker** & **docker-compose**
* **k6** (for load testing)
* Git and access to group repository

---

## 3. Installation & Configuration

1. **Clone repository**:

   ```bash
   git clone <repo-url> fitco
   cd fitco
   ```
2. **Python environment**:

   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Environment variables**: copy `.env.example` → `.env` and set:

   ```ini
   FLASK_ENV=development
   DATABASE_URL=postgresql://user:pass@localhost:5432/fitco
   AI_API_KEY=<your-key>
   STRIP_API_KEY=<your-key>
   ```
4. **Initialize database**:

   ```bash
   flask db upgrade           # Apply migrations
   python -c "from src.fit.db_init import init_fitness_data; init_fitness_data()"
   ```
5. **Run server**:

   ```bash
   flask run --host 0.0.0.0 --port 5000
   ```

---

## 4. Application Architecture

### Directory Structure

```text
fitco/
├── src/fit/
│   ├── __init__.py
│   ├── app.py             # Flask app factory
│   ├── blueprints/
│   │   ├── auth.py
│   │   ├── workout.py
│   │   ├── nutrition.py
│   │   └── payments.py
│   ├── models/            # SQLAlchemy models
│   ├── services/          # Business logic, Pydantic schemas
│   ├── tests/             # pytest files
│   └── db_init_scripts/   # SQL for initial data
├── Dockerfile
├── docker-compose.yml
├── k6/                    # Load test scripts
├── adr/
│   └── 02-coach-service-migration.md
├── requirements.txt
└── .env.example
```

### Flask Blueprints & Endpoints

|   Blueprint | Prefix       |                 Endpoint |  Method  | Description                                  |
| ----------: | ------------ | -----------------------: | :------: | -------------------------------------------- |
|      `auth` | `/auth`      |    `/login`, `/register` |   POST   | User authentication                          |
|   `workout` | `/workout`   |       `/wod`, `/history` | GET/POST | Generate WOD (POST `/wod`), retrieve history |
| `nutrition` | `/nutrition` |                  `/plan` |    GET   | Dietary guidance                             |
|  `payments` | `/payments`  | `/subscribe`, `/webhook` |   POST   | Handle premium upgrades & Stripe webhooks    |

---

## 5. Database Schema & Data Initialization

### Muscle Groups

|        Column |         Type | Description              |
| ------------: | -----------: | ------------------------ |
|          `id` |       SERIAL | PK                       |
|        `name` | VARCHAR(100) | Unique muscle group name |
|   `body_part` |  VARCHAR(50) | Body region              |
| `description` |         TEXT | Details                  |

### Exercises

|         Column |         Type | Description          |
| -------------: | -----------: | -------------------- |
|           `id` |       SERIAL | PK                   |
|         `name` | VARCHAR(100) | Unique exercise name |
|  `description` |         TEXT | Overview             |
|   `difficulty` |          INT | 1 (easy)–5 (hard)    |
|    `equipment` | VARCHAR(100) | Required gear        |
| `instructions` |         TEXT | Step-by-step guide   |

### Exercise–Muscle Groups Mapping

|            Column |    Type | Description              |
| ----------------: | ------: | ------------------------ |
|     `exercise_id` | INTEGER | FK → `exercises.id`      |
| `muscle_group_id` | INTEGER | FK → `muscle_groups.id`  |
|      `is_primary` | BOOLEAN | Primary muscle indicator |

### Initialization Script

* Located at `src/fit/db_init_scripts/init_muscle_groups_exercises.sql`
* Creates tables if absent.
* Populates default muscle groups & exercises.
* Run on startup via `init_fitness_data()`.

---

## 6. Service Layer & Pydantic Models

Service functions in `services/fitness_service.py`:

* `get_all_muscle_groups()` → `List[MuscleGroupSchema]`
* `get_muscle_group_by_id(id)` → `MuscleGroupSchema`
* `get_all_exercises()` → includes nested muscle groups
* `get_exercises_by_muscle_group(id)`
* `get_exercise_by_id(id)`

Schemas in `services/schemas.py` mirror DB models with validation.

---

## 7. Testing

### Unit & Integration Tests

* Located under `src/fit/tests/`
* Use `pytest` and `pytest-flask`.
* Mock external AI & Stripe calls via fixtures.

### Fixing the Failing Test

1. Identify failure: run `pytest -q --maxfail=1`.
2. Inspect stack trace; adjust code or test.
3. Commit fix and confirm all tests pass.

---

## 8. Containerization (Docker)

### Dockerfile

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/src/
COPY entrypoint.sh /app/
ENTRYPOINT ["/app/entrypoint.sh"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: fitco
  web:
    build: .
    env_file: .env
    ports:
      - "5000:5000"
    depends_on:
      - db
```

---

## 9. Load Testing (k6)

### Writing & Running k6 Scripts

* Scripts in `/k6/wod_load_test.js`.
* Example:

  ```js
  import http from 'k6/http';
  import { check } from 'k6';
  export let options = { vus: 50, duration: '1m' };
  export default function() {
    let res = http.post('http://localhost:5000/workout/wod', { userId: 1 });
    check(res, { 'status 200': r => r.status === 200 });
  }
  ```
* Run: `k6 run k6/wod_load_test.js`

### Interpreting Results

* Observe `max VUs` before failure or latency > 1s.
* Use metrics: `http_req_duration`, `vus_max`.
* Document findings in `k6/results.md`.

---

## 10. Microservice: `coach`

### Responsibility & Scope

* Handles only WOD generation (`/generate`).
* Stateless; does **not** persist history.
* Communicates with main app via REST.

### API Specification

|          Endpoint | Method | Request Body        | Response              |
| ----------------: | :----: | ------------------- | --------------------- |
| `/coach/generate` |  POST  | `{ userId, goals }` | `{ workouts: [...] }` |

### Strangler Fig Migration

1. Deploy `coach` at `/coach/...` alongside monolith.
2. In `workout` blueprint, route `/wod` toggles between monolith and coach based on header or config flag.
3. Gradually shift traffic.
4. Deprecate monolith logic when 100% traffic uses `coach`.

### ADR: Migration Design Document

* Located at `adr/02-coach-service-migration.md`.
* Summarizes: load estimates, team impact, rollback plan, staging rollout.

---

## 11. Environment Variables

|             Name | Description                          |
| ---------------: | ------------------------------------ |
|   `DATABASE_URL` | PostgreSQL connection URL            |
|     `AI_API_KEY` | External AI provider credential      |
| `STRIPE_API_KEY` | Stripe secret key for payments       |
|   `USE_COACH_MS` | `true` to route WOD to coach service |

---

## 12. Deployment & CI/CD

* CI: GitHub Actions runs lint, pytest, build Docker image.
* CD: On merge to `main`, push image to registry; deploy to Kubernetes cluster.
* Healthchecks: `/health` on both services.

---

## 13. Contact & Delivery

* **Design doc (ADR)**: `adr/02-coach-service-migration.md`.
* **Repo link**: share via email to instructor.
* **Deadline**: Monday, May 26, 2025 20:00 UTC.
