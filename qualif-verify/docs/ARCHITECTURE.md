# System Architecture & Design Decisions

## Overview

```
Browser / client
   |  HTTP (JSON)
   v
FastAPI (REST API under /api/v1)   <-- Pydantic validation rules
   |
   |-- routes: register / search / verify / revoke / audit
   |-- service: HMAC-SHA256 integrity signatures (verification core)
   +-- SQLAlchemy 2 ORM
          |
          v
     SQLite (dev/demo) --> PostgreSQL (scale-up path)

DevOps sidecar:
  GitHub Actions:  lint (ruff) --> tests (pytest + coverage gate)
                   --> docker build (main only) --> deploy (main only)
```

## Key decisions (with justification — feed the technical report)

1. **FastAPI over Flask/Django.** Auto-generated OpenAPI docs (usability +
   demo), Pydantic gives declarative validation rules that *double as* the R1
   validation tests, and typed dependencies keep auth/DB logic unit-testable.
2. **HMAC-SHA256 integrity signature per record (the verification core).**
   Every record is signed over all its fields with a server secret;
   verification = recompute and compare. Detects tampering without exposing
   the secret, and is trivially unit-testable. A blockchain bonus would add
   cross-organisation trust on top (see roadmap).
3. **SQLite + SQLAlchemy.** Zero-ops for the demo; the ORM abstracts the
   database so PostgreSQL is a config change, not a rewrite.
4. **Append-only audit table.** `AuditLog` has no update/delete API; every
   action (registration, search, verify success/failure, revocation) is
   logged with actor + timestamp → R4.
5. **Header-based roles (`X-Role` / `X-User`) — a deliberate limitation.**
   Keeps the demo frictionless for the marker. The report's critical
   evaluation should weigh this against real JWT/OAuth2 and argue the
   upgrade path. (Swapping in JWT is itself a bonus opportunity.)
6. **Monolith, not microservices.** Four requirements, one team, one
   container — KISS, justified with YAGNI.

## Bonus roadmap (up to 10 extra marks)

- **Agentic AI:** a "verification assistant" endpoint that explains verify
  results in plain language and flags anomalies (e.g. bulk lookups).
- **Blockchain:** anchor each registration's hash to a testnet →
  tamper-evident credentials across institutions.
- **Advanced security:** JWT + RBAC, rate limiting, signed requests.
- **Monitoring:** `/metrics` endpoint + Prometheus/Grafana dashboard.
- **IaC:** Terraform/Pulumi, or docker-compose + Actions-managed deploy.
