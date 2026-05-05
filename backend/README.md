# Backend Phase 1 Scaffold

This directory contains the shared FastAPI shell for Phase 1. It is intentionally limited to the backend application entrypoint, configuration, transport schemas, database session foundation, route wiring, and test scaffolding needed by the first batch of APIs.

## Current Scope

- FastAPI application factory and system endpoints
- shared settings and logging bootstrap
- unified `api/v1` router registration
- shared response envelope and schema primitives
- SQLAlchemy engine, metadata, and session foundation
- reserved domain module packages for overview, twin, and detection
- test skeleton for the backend shell

## Explicitly Out Of Scope

- knowledge, screen, or other Phase 2+ route groups
- worker execution, Celery, Redis jobs, object storage, or model inference
- Docker, containers, or external infrastructure bootstrapping
- frontend page changes

## Layout

```text
backend/
  app/
    main.py
    core/
      config.py
      logging.py
    api/
      deps.py
      v1/
        router.py
    db/
      base.py
      session.py
    modules/
      overview/
      twin/
      detection/
    schemas/
      common.py
  tests/
    conftest.py
    test_app.py
  .env.example
  README.md
```

## Shared Contract

All Phase 1 endpoints should return the shared transport envelope from `backend/app/schemas/common.py`:

```json
{
  "code": "OK",
  "message": "",
  "requestId": "uuid",
  "data": {}
}
```

The envelope is transport-level only. Domain models inside feature modules should remain structured and should not store frontend presentation strings as their core fields.

## Route Wiring

`backend/app/api/v1/router.py` auto-discovers route modules under `backend/app/api/v1/`. Feature modules only need to add a file that exports an `APIRouter` named `router`.

Reserved Phase 1 route files:

- `backend/app/api/v1/overview.py`
- `backend/app/api/v1/twin.py`
- `backend/app/api/v1/detection.py`

Reserved Phase 1 module packages:

- `backend/app/modules/overview/`
- `backend/app/modules/twin/`
- `backend/app/modules/detection/`

Reserved Phase 1 endpoints:

- `GET /api/v1/pages/overview`
- `GET /api/v1/pages/twin`
- `POST /api/v1/detection/batches`
- `GET /api/v1/detection/batches/{id}`

Shared shell endpoints:

- `GET /healthz`
- `GET /api/v1`

`GET /api/v1` exposes the current router registry and shows whether the reserved Phase 1 route files have been mounted yet. This lets feature modules attach independently without changing `main.py`.

The registry also exposes the expected domain package for each slot so feature modules can keep business logic isolated under `backend/app/modules/<feature>/`.

## Local Run

1. Copy `backend/.env.example` to `backend/.env`.
2. Install the Python dependencies required by the backend shell.
3. Start the app from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

Suggested packages for this scaffold:

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pydantic-settings`
- `pytest`

## Notes For Feature Modules

- Keep business logic outside `backend/app/main.py`.
- Reuse `backend/app/api/deps.py` for settings, request ID, and DB session dependencies.
- Reuse `backend/app/schemas/common.py` for response envelopes and base schema behavior.
- Reuse `backend/app/db/base.py` for declarative metadata and shared timestamp columns.
- Keep route files thin; put page and domain assembly in the feature module directory.
