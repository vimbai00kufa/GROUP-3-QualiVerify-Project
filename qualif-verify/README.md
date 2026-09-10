# Qualification Verification System (QVS)

**MIM736 Practical Assignment** — skeleton only, simple texts, no logic.

## The four core requirements

| # | Requirement | Endpoint |
|---|---|---|
| R1 | Register qualifications (admin) | `POST /api/v1/qualifications` |
| R2 | Search & retrieve records (verifier/admin) | `GET /api/v1/qualifications?query=...` |
| R3 | Verify authenticity (public) | `POST /api/v1/verify` |
| R4 | Auditable history (admin) | `GET /api/v1/audit` |

## Quickstart (local)

```bash
pip install -r requirements.txt -r requirements-dev.txt

# run the API (docs at http://127.0.0.1:8000/docs)
uvicorn main:app --reload

# run the tests
pytest
```

All routes return simple placeholder texts. Team adds real logic later.

## Repository layout

```
qualif-verify/
├── .github/
│   ├── workflows/ci-cd.yml
│   ├── ISSUE_TEMPLATE.md
│   └── pull_request_template.md
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── service.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BRANCHING.md
│   ├── CONFLICT_LOG.md
│   ├── REQUIREMENTS_MATRIX.md
│   ├── TEAM_PLAN.md
│   └── evidence/
├── Dockerfile
├── main.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```
