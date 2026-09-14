"""Role-based access control (RBAC): role definitions and permission dependencies.

Design notes (full write-up in docs/RBAC.md):

- **Authentication** is simulated via the ``X-User`` / ``X-Role`` request
  headers, matching the limitation already documented in
  ``docs/ARCHITECTURE.md`` (#5). This module is the single place a future
  JWT/OAuth2 upgrade would plug into -- only the header lookup below would
  change, every route would keep working unmodified.
- **Authorisation** is enforced here, server-side, as a FastAPI dependency on
  every protected route. There is no client-side/template-only enforcement:
  a request with a missing or insufficient role is rejected before any route
  handler code runs.
- Authentication failures (no role supplied, or a role the system does not
  recognise) return **401 Unauthorized**. Authorisation failures (a real,
  recognised role that is simply not permitted to perform the action) return
  **403 Forbidden**. Keeping these distinct matches the "authentication
  before authorisation" requirement and gives callers/tests an unambiguous
  signal.
"""

from fastapi import Header, HTTPException


class Role:
    """The four roles required by the RBAC feature (see docs/RBAC.md)."""

    ADMINISTRATOR = "administrator"
    REGISTRAR = "registrar"
    VERIFICATION_OFFICER = "verification_officer"
    STANDARD_USER = "standard_user"


ALL_ROLES = frozenset(
    {
        Role.ADMINISTRATOR,
        Role.REGISTRAR,
        Role.VERIFICATION_OFFICER,
        Role.STANDARD_USER,
    }
)


def current_actor(x_user: str = Header(default="anonymous")) -> str:
    """The identity of the caller, for audit logging (see ARCHITECTURE.md #5)."""
    return x_user or "anonymous"


def require_role(*allowed_roles: str):
    """Dependency factory: authenticate the caller, then authorise their role.

    Usage::

        role: str = Depends(require_role(Role.ADMINISTRATOR, Role.REGISTRAR))

    Raises:
        401 if the ``X-Role`` header is missing or is not one of the four
            recognised roles (authentication failure).
        403 if the role is recognised but not in ``allowed_roles``
            (authorisation failure).
    """
    allowed = set(allowed_roles)
    if not allowed.issubset(ALL_ROLES):
        raise ValueError(f"Unknown role(s) in require_role(...): {allowed - ALL_ROLES}")

    def _dependency(x_role: str = Header(default="")) -> str:
        if not x_role:
            raise HTTPException(
                status_code=401,
                detail="Authentication required: missing X-Role header",
            )
        if x_role not in ALL_ROLES:
            raise HTTPException(status_code=401, detail=f"Unrecognised role: {x_role!r}")
        if x_role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{x_role}' is not permitted to perform this action",
            )
        return x_role

    return _dependency


def require_any_role():
    """Any authenticated (recognised) role -- used for functions open to all four roles."""
    return require_role(*ALL_ROLES)
