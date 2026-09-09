# Requirements → Verification Matrix

This matrix is the spine of the "Automated Verification of Requirements"
section. Every requirement maps to concrete test cases that run in CI; the
pipeline **fails the build** if any of them fails (quality gate).

| Req | Requirement | Test cases (file::test) | CI gate | Evidence |
|---|---|---|---|---|
| R1 | Register qualifications (admin only) | `test_api.py::test_register_success`, `::test_register_requires_admin_role`, `::test_register_rejects_duplicate_certificate`, `test_schemas.py::*` (validation rules) | `test` job (green required for merge) | Pipeline run screenshot + coverage artifact |
| R2 | Search & retrieve records | `test_api.py::test_search_finds_registered_record`, `::test_search_returns_empty_list_when_no_match`, `::test_search_requires_role` | same | same |
| R3 | Verify authenticity | `test_api.py::test_verify_valid_qualification`, `::test_verify_rejects_wrong_holder_name`, `::test_verify_unknown_certificate`, `::test_verify_rejects_revoked_qualification`, `test_service.py::*` (integrity) | same | same |
| R4 | Auditable history | `test_api.py::test_audit_log_records_activity`, `::test_audit_requires_admin` | same | same |
| NF1 | Integrity / security (HMAC signature) | `test_service.py::test_signature_*`, `test_verify_integrity_detects_tampering` | lint + test jobs | unit test report |
| NF2 | Code quality & coverage ≥ 80% | `pytest --cov-fail-under=80` | coverage gate in CI | coverage.xml artifact |
| NF3 | Deployable & reproducible | Docker image builds in pipeline | `docker` job | build log + live URL |
| NF4 | Coding standards | `ruff check` + `ruff format --check` | `lint` job (blocks merge) | lint log |
| NF5 | Role-based access control (4 roles) | `test_rbac.py::*` (role, authentication, authorisation-matrix, negative/security, regression tests), see `docs/RBAC.md` | `test` job (green required for merge) | Pipeline run screenshot + coverage artifact |

**How a requirement is "automatically verified":** the moment a PR touches
code, GitHub Actions runs lint → tests → coverage. A broken requirement fails
the job, the PR cannot merge, and a bad release cannot be built.

Keep pipeline-run screenshots in `docs/evidence/` — they go straight into the
technical report and the demo video.
