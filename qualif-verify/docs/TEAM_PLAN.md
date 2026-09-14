# Team Plan & Task Allocation

Five roles (re-assign rows if you have 3–4 people — see "Variations").
Everyone writes code and tests; the roles define *accountability*, not silos.

## Roles

| Role | Person | Accountable for |
|---|---|---|
| **Tech Lead / Backend** | ? | Architecture, data model, API routes, verification service |
| **Frontend / UX** | ? | Web UI, usability, demo quality |
| **QA / Test Lead** | ? | Test suite, coverage ≥ 80%, static analysis, requirements matrix |
| **DevOps Lead** | ? | CI/CD pipeline, Docker, deployment, environment secrets |
| **PM / Docs** | ? | Issue board, technical report, demo video, viva prep, contribution reports |

## Task allocation (each task = one GitHub issue)

| Task | Owner | Support | Due (wk) |
|---|---|---|---|
| T1 Create repo, invite team, configure Actions | DevOps | PM | 1 |
| T2 Set up CI lint + test pipeline (green on push) | DevOps | QA | 1 |
| T3 Write requirements + requirements matrix | PM | QA | 1 |
| T4 Data model + DB (Qualification, AuditLog) | Backend | QA | 1 |
| T5 Verification service (HMAC signature) + unit tests | Backend | QA | 2 |
| T6 Registration endpoint + validation rules | Backend | QA | 2 |
| T7 Search endpoint | Backend | Frontend | 2 |
| T8 Verify endpoint | Backend | QA | 2 |
| T9 Audit log + endpoint | Backend | QA | 2 |
| T10 Revoke endpoint | Backend | QA | 3 |
| T11 Integration tests for all requirements | QA | Backend | 3 |
| T12 Coverage ≥ 80% + ruff clean + CI quality gates | QA | DevOps | 3 |
| T13 Web UI (register/search/verify/audit pages) | Frontend | Backend | 3 |
| T14 Dockerfile + docker-compose + deploy to live server | DevOps | Backend | 4 |
| T15 Merge-conflict drill (documented in docs/CONFLICT_LOG.md) | All | PM | 2 |
| T16 Technical report (3,000–4,000 words) | PM (leads) | All | 4 |
| T17 Demo video (10–15 min) | Frontend | All | 4 |
| T18 Individual contribution reports | All | PM | 4 |
| T19 Viva rehearsal | All | PM | 4 |

## Four-week milestones

- **Week 1 — Foundation:** repo + CI green, requirements frozen, issues created, data model done.
- **Week 2 — Core build:** all four requirements implemented + unit tests; conflict drill done.
- **Week 3 — Quality:** integration tests, coverage gate, UI, static analysis clean.
- **Week 4 — Ship:** Docker deploy live, report, video, viva rehearsal, contribution reports.

## 3–4 person variations

- **4 people:** merge Frontend into Backend; PM keeps report + issues.
- **3 people:** Backend (+UI), QA (+CI/DevOps), PM (+reports/video). QA also owns the pipeline.

## Rules of engagement

- No task is "done" without: code on a feature branch, tests passing in CI, a merged PR with at least one review, and the issue closed.
- Daily 15-minute standup (async in a #standup thread is fine).
- Any team member can review any PR; reviews turn around in < 24 h.
- Keep `docs/REQUIREMENTS_MATRIX.md` current — it is the spine of the report.
