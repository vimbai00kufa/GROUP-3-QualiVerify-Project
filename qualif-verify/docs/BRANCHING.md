# Git Workflow & Branching Strategy

## Branches

| Branch | Purpose | Protection |
|---|---|---|
| `main` | Always deployable; tagged releases | CI must pass; PRs only |
| `develop` | Integration branch for features | CI must pass; PRs only |
| `feature/<issue>-<short-desc>` | One task each, e.g. `feature/6-verify-endpoint` | — |
| `fix/<issue>-<short-desc>` | Bug fixes from develop | — |

## The daily flow

1. `git checkout develop && git pull`
2. `git checkout -b feature/6-verify-endpoint`
3. Work in **small, meaningful commits** (see convention below).
4. `git push -u origin feature/6-verify-endpoint` → open a **pull request** to `develop`.
5. CI must be green; **one teammate approves** the code review.
6. Squash-merge (keeps `develop` history readable).
7. Weekly: `develop` → `main` PR (release). `main` triggers Docker build + deploy.

## Commit message convention

`type: short imperative summary` (≤ 72 chars)

- `feat:` new feature · `fix:` bug fix · `test:` tests only
- `docs:` documentation · `refactor:` no behaviour change · `chore:` build/CI/tooling

Examples:

- `feat: add certificate registration endpoint`
- `test: integration tests for verification flow (R3)`
- `chore: add coverage gate to CI pipeline`

## Pull request rules

- Title = one sentence; body uses `.github/pull_request_template.md`.
- Must link an issue (`Closes #6`) and include a **screenshot of the green CI run**.
- At least one approving review before merge.
- Keep PRs small (< ~300 lines) so reviews are fast.

## Merge-conflict drill (required evidence)

Two teammates deliberately create and resolve a conflict; the resolution is
logged in `docs/CONFLICT_LOG.md` with screenshots:

1. Teammates A and B both branch from `develop` and edit the **same lines** of `app/routes.py`.
2. A merges first (PR approved, green CI).
3. B rebases onto `develop`, hits the conflict, resolves it **by hand**, pushes; A reviews the resolution in the PR.
4. Log: who, when, what conflicted, how it was resolved, and why.

## Issue workflow

- Every task in `TEAM_PLAN.md` gets an issue *before* work starts.
- Labels: `backend`, `frontend`, `qa`, `devops`, `docs`.
- Assignee = the owner; the issue is closed by the merged PR (`Closes #n`).
