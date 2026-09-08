# Qualification Verification System (QVS)

**MIM736 Practical Assignment** — a DevOps-enabled qualification verification
system. A web API that lets authorised users register qualifications, search
records, verify the authenticity of a qualification, and review a
tamper-evident audit history of all verification activity.

> **Team starter kit.** This is the skeleton your team builds on. The graded
> work — commits, pull requests, reviews, conflicts, the report and the video
> — must be produced by *your* team on *your* repository. Do not present this
> initial state as your own work.

## The four core requirements

| # | Requirement | Endpoint |
|---|---|---|
| R1 | Register qualifications (admin) | `POST /api/v1/qualifications` |
| R2 | Search & retrieve records (verifier/admin) | `GET /api/v1/qualifications?query=...` |
| R3 | Verify authenticity (public) | `POST /api/v1/verify` |
| R4 | Auditable history (admin) | `GET /api/v1/audit` |

## Tech stack

- **Python 3.10+**, FastAPI, SQLAlchemy 2, SQLite (swap to PostgreSQL to scale)
- **pytest + pytest-cov** — unit + integration tests, coverage gate ≥ 80%
- **ruff** — lint + format, enforced as a CI quality gate
- **Docker** — containerised deployment
- **GitHub Actions** — CI/CD pipeline (`.github/workflows/ci-cd.yml`)

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# run the API (interactive docs at http://127.0.0.1:8000/docs)
uvicorn main:app --reload

# run the tests
pytest --cov=app --cov-report=term-missing
```

Roles are passed via headers for the demo: `X-Role: admin|verifier` and
`X-User: <name>` (see `docs/ARCHITECTURE.md` for the trade-off discussion).

## Team getting-started checklist (Day 1)

1. Create a **private** GitHub repo for the team and add all members.
2. Push this scaffold as the **first commit(s)** — one slice per person.
3. Read `docs/TEAM_PLAN.md` and create **one issue per task** (assign owners).
4. Agree on the branching rules in `docs/BRANCHING.md` before writing code.
5. Watch the CI pipeline run on the first push — it is your quality gate.
6. Keep `docs/REQUIREMENTS_MATRIX.md` updated as tests are written.

## Repository layout

```
qualif-verify/
├── .github/
│   ├── workflows/ci-cd.yml       # CI/CD: lint → test → docker → deploy
│   ├── ISSUE_TEMPLATE.md
│   └── pull_request_template.md
├── app/
│   ├── __init__.py               # app factory
│   ├── config.py                 # env-driven settings
│   ├── database.py               # engine/session helpers
│   ├── models.py                 # Qualification + AuditLog
│   ├── routes.py                 # REST API (R1-R4 + revoke)
│   ├── schemas.py                # validation rules (Pydantic)
│   └── service.py                # HMAC verification core
├── tests/
│   ├── conftest.py               # fresh app + DB per test
│   ├── unit/                     # service + validation tests
│   └── integration/              # end-to-end API tests (R1-R4)
├── docs/
│   ├── ARCHITECTURE.md           # design decisions + bonus roadmap
│   ├── BRANCHING.md              # git workflow + conflict drill
│   ├── CONFLICT_LOG.md           # evidence of conflict resolution
│   ├── REQUIREMENTS_MATRIX.md    # requirement → test → gate
│   ├── TEAM_PLAN.md              # roles, tasks, milestones
│   └── evidence/                 # pipeline screenshots for the report
├── Dockerfile
├── main.py                       # uvicorn entry point
├── pyproject.toml                # ruff + pytest config
├── requirements.txt
└── requirements-dev.txt
```

## Design notes

See `docs/ARCHITECTURE.md` for the architecture and the critical evaluation
of key decisions (HMAC integrity signatures, role-based header auth, SQLite,
and where the optional bonus features fit).
