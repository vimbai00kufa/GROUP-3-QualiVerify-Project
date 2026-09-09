# Role-Based Access Control (RBAC)

Feature branch: `feature/role-based-access-control` (branch from `develop`,
per `docs/BRANCHING.md`).

## 1. Requirement analysis

The assignment requires four roles — Administrator, Institution/Registrar,
Verification Officer, Standard User — each restricted to the functions it is
permitted to perform, with unauthorised access rejected and access-control
tests in place.

**Assumptions made about the existing project** (confirmed by inspecting
the actual skeleton, not assumed):

- The project is **FastAPI + SQLAlchemy 2 + Pydantic**, not Django. There is
  no Django `User`/`Group`/`Permission` system to reuse; RBAC is built as
  FastAPI dependencies instead — the idiomatic equivalent of Django
  decorators/mixins for this stack.
- There is **no persistent `User` model or login system**. Caller identity
  and role are already simulated via the `X-User` / `X-Role` request
  headers (see `docs/ARCHITECTURE.md` point 5, which explicitly flags this
  as a documented demo limitation with a JWT/OAuth2 upgrade path). This
  feature extends that existing mechanism from a binary `admin`/`verifier`
  check to the full four-role model, rather than inventing a new
  authentication system that would be out of scope for this task.
- There is **no institution field** on `Qualification` records, so
  object-level "only see your own institution's records" restrictions are
  not implemented. This is called out below as a known limitation and
  roadmap item.
- "Manage users" / "assign roles" (an Administrator capability in the
  assignment brief) has no corresponding feature in this system because
  there is no user store — roles are asserted per-request via the header.
  Administrator-only enforcement is still demonstrated on every existing
  privileged endpoint.

## 2. RBAC permission matrix

| Function                              | Administrator | Registrar | Verification Officer | Standard User |
| -------------------------------------- | :-----------: | :-------: | :-------------------: | :------------: |
| Register qualification (`POST /qualifications`) | Allow | Allow | Deny | Deny |
| Search / view records (`GET /qualifications`)    | Allow | Allow | Allow | Allow |
| Verify qualification (`POST /verify`)            | Allow (public) | Allow (public) | Allow (public) | Allow (public) |
| Revoke qualification (`POST /qualifications/{id}/revoke`) | Allow | Deny | Deny | Deny |
| View audit history (`GET /audit`)                | Allow | Deny | Allow | Deny |

Notes:

- **Verification is intentionally public/unauthenticated.** The system's
  entire purpose is to let anyone check a certificate; gating it behind a
  role would contradict requirement R3. This is a deliberate design
  decision, not an oversight — see the docstring on `verify_qualification`
  in `app/routes.py`.
- **Registrar can register but not revoke.** Revocation is a higher-impact,
  harder-to-reverse action than registration, so it is kept
  Administrator-only even though a Registrar issues qualifications.
- **Verification Officer can read the audit trail** (to review past
  verification decisions) but cannot register or revoke records.

## 3. Recommended architecture

RBAC is implemented as a small, dependency-injected module,
`app/roles.py`, following the pattern FastAPI itself recommends and that
this project's own `routes.py` already used (`require_admin`/
`require_verifier`) before this feature generalised it:

- `Role` — string constants for the four roles (`administrator`,
  `registrar`, `verification_officer`, `standard_user`).
- `require_role(*allowed_roles)` — a dependency **factory**. Each protected
  route declares exactly which roles may call it, e.g.
  `Depends(require_role(Role.ADMINISTRATOR, Role.REGISTRAR))`. FastAPI
  resolves and runs this before the route body executes, so an
  unauthorised request never reaches business logic.
- `require_any_role()` — sugar for "any of the four roles", used by the
  search endpoint, which is open to all authenticated roles.
- `current_actor` — unchanged identity lookup (`X-User` header), moved into
  the same module for cohesion.

This was chosen over alternatives considered:

- **A custom `User` model + DB-backed roles** — rejected as out of scope:
  the assignment's acceptance criteria concern the RBAC *decision logic*
  and its enforcement/testing, and the project deliberately has no login
  system to attach it to. Building one would be "unnecessarily rewriting
  existing project architecture," which the brief explicitly says to
  avoid.
- **Checking roles inline in each route body** — rejected because it is
  easy to forget on a new route and hard to unit test in isolation;
  dependency injection makes the check impossible to bypass accidentally
  and testable on its own (see `tests/integration/test_rbac.py`).

**Integration with future qualification-verification apps:** any new route
just adds `Depends(require_role(...))` with the roles it needs — no changes
to `app/roles.py` are required unless a fifth role is introduced.

## 4. Authentication vs authorisation

- **401 Unauthorized** — no `X-Role` header supplied, or the value supplied
  is not one of the four recognised roles. This is an *authentication*
  failure: the system doesn't know who/what is calling.
- **403 Forbidden** — a real, recognised role was supplied, but it isn't
  permitted to perform the requested action. This is an *authorisation*
  failure.

Keeping these distinct (rather than returning 403 for everything, as the
original `require_admin`/`require_verifier` helpers did) matches the
assignment's explicit "authentication before authorisation" requirement and
gives both API consumers and tests an unambiguous signal.

## 5. Security considerations

- **Server-side enforcement only.** All checks run in FastAPI dependencies
  on the backend; nothing relies on hiding UI elements. The static web UI in
  `app/static/` has no bearing on what the API will accept.
- **No privilege escalation via the request body.** Enforcement reads only
  the `X-Role` header; a request that stuffs `"role": "administrator"` or
  `"is_admin": true` into the JSON payload is ignored and still gets 403 if
  the caller's real role doesn't permit the action (see
  `test_role_cannot_be_self_escalated_via_request_body`).
- **CSRF / password handling** — not applicable: this is a stateless JSON
  API with no cookie-based sessions or password storage to protect.
- **Object-level access** — not implemented; see the "assumptions" and
  "roadmap" sections. Every Registrar currently sees every institution's
  records, which is acceptable for the demo scope but should be called out
  as a limitation in the technical report.
- **Audit logging** — registration, search, verification and revocation
  are already logged with actor + timestamp (`AuditLog`, unchanged by this
  feature). Logging denied/forbidden attempts is listed as a roadmap item
  below rather than added here, to keep this PR focused and reviewable.

## 6. Roadmap / known limitations

- Add an `institution` field to `Qualification` and enforce object-level
  scoping so a Registrar only manages their own institution's records.
- Replace the `X-Role` / `X-User` header scheme with real authentication
  (JWT/OAuth2), swapping only the header-parsing code inside `app/roles.py`
  — every route's `Depends(require_role(...))` call stays unchanged.
- Log denied/forbidden authorisation attempts to the audit trail.

## 7. Automated tests

All RBAC tests live in `tests/integration/test_rbac.py`, plus targeted
updates to `tests/integration/test_api.py` and `tests/conftest.py`
(headers for all four roles). Coverage includes:

- **Role tests** — all four roles exist and are distinct
  (`test_all_four_roles_exist`); each role authenticates successfully
  (`test_role_can_be_assigned_via_header_and_is_accepted`, parametrised).
- **Authentication tests** — missing header and unrecognised role both
  return 401 on every protected endpoint
  (`test_unauthenticated_request_rejected_on_every_protected_endpoint`,
  `test_unrecognised_role_is_rejected_as_unauthenticated`).
- **Authorisation matrix** — every role against every protected function,
  parametrised directly from the tables in §2
  (`test_register_authorisation_matrix`, `test_search_authorisation_matrix`,
  `test_revoke_authorisation_matrix`, `test_audit_authorisation_matrix`),
  plus a check that `/verify` stays public for everyone
  (`test_verify_is_public_for_every_role_and_for_no_role`).
- **Negative / security tests** — a Standard User cannot reach
  Administrator functions; a Registrar cannot manage audit/revoke; a
  Verification Officer cannot register or revoke; a role claim smuggled
  into the request body cannot escalate privilege; every protected endpoint
  rejects a fully unauthenticated request.
- **Regression test** — a full register → search → verify → audit workflow
  with correctly-permitted roles still passes end to end
  (`test_full_workflow_still_works_end_to_end_with_correct_roles`).

Run locally:

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

## 8. Ruff / code quality

```bash
ruff check app/ tests/
ruff format --check app/ tests/
```

Both pass cleanly on the RBAC changes (`app/roles.py`, updated
`app/routes.py`, `tests/conftest.py`, `tests/integration/test_api.py`,
new `tests/integration/test_rbac.py`).

## 9. CI/CD integration

No changes to `.github/workflows/ci-cd.yml` were required: the existing
`lint` job already runs `ruff check`/`ruff format --check` over `app/` and
`tests/`, and the existing `test` job already runs the full `pytest` suite
with the `--cov-fail-under=80` gate — the new RBAC files are picked up
automatically because they live inside those same directories.

## 10. Git workflow

```bash
git checkout develop && git pull
git checkout -b feature/role-based-access-control
# implement, run pytest + ruff locally
git add app/roles.py app/routes.py tests/conftest.py \
        tests/integration/test_api.py tests/integration/test_rbac.py \
        docs/RBAC.md
git commit -m "feat: add role-based access control for four system roles"
git commit -m "test: add RBAC authentication and authorisation matrix tests"
git commit -m "docs: document RBAC architecture, matrix and assumptions"
git push -u origin feature/role-based-access-control
# open PR to develop, link the RBAC issue, wait for green CI + 1 review, merge
```

Do not push directly to `main` or `develop`.

## 11. Assignment evidence checklist

Capture and store under `docs/evidence/`:

- [ ] Feature branch + commit history for `feature/role-based-access-control`.
- [ ] Pull Request to `develop` with a linked issue and a green-CI screenshot.
- [ ] Code review comments/approval on the PR.
- [ ] GitHub Actions run: `lint` and `test` jobs both green.
- [ ] `pytest` output showing all RBAC tests passing.
- [ ] Coverage report (`coverage.xml` artifact / terminal report) ≥ 80%.
- [ ] `ruff check` / `ruff format --check` clean output.
- [ ] A manual request per role (e.g. via `/docs` Swagger UI or `curl` with
      `X-Role`/`X-User` headers) showing an allowed call succeeding and a
      denied call returning 401/403.

## 12. Final verification checklist

| Acceptance criterion | Status |
| --- | --- |
| Roles are represented in the system | ✅ `app/roles.py::Role` |
| Users can only access functions permitted for their role | ✅ enforced via `require_role`/`require_any_role` on every protected route |
| Unauthorised access is rejected | ✅ 401 (unauthenticated) / 403 (unauthorised), see §4 |
| Access-control tests exist | ✅ `tests/integration/test_rbac.py` + updated `test_api.py` |
