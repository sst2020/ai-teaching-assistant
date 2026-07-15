# Repository Structure

## Goal

This repository should read like a small workspace with two applications, not a root-level dumping ground. Source-of-truth code lives in app directories; the root is reserved for orchestration and shared documentation.

## Top-Level Layout

| Path | Role | Notes |
|------|------|-------|
| `backend/` | FastAPI backend | API routes, services, models, migrations, backend scripts, backend tests. |
| `frontend/` | React frontend | Components, pages, hooks, i18n, frontend tests, frontend build config. |
| `docs/` | Stable docs | Setup, product docs, reports, TODO index, and governed planning artifacts. |
| `issues/` | Backlog notes | Feature proposals or issue writeups that are not product code. |
| `scripts/` | Workspace helpers | Thin root-level wrappers such as dev startup and environment checks. |
| `temp/` | Scratch space | Local-only and ignored. |
| `outputs/runtime/` | Runtime receipts | Local-only `vibe` evidence and other generated receipts, ignored. |

## Documentation Layout

| Path | Role |
|------|------|
| `docs/DEVELOPMENT_SETUP.md` | Authoritative setup and debugging guide |
| `docs/REPOSITORY_STRUCTURE.md` | This ownership and placement document |
| `docs/TODO.md` | Index for roadmap docs |
| `docs/TODO.en.md` | English roadmap |
| `docs/TODO.zh-CN.md` | Chinese roadmap |
| `docs/requirements/` | Frozen governed requirement docs |
| `docs/plans/` | Frozen governed execution plans |

## Placement Rules

1. New application code belongs in `backend/` or `frontend/`.
2. The repository root should not host a second frontend, a second backend, or ad hoc test scripts.
3. Root scripts may orchestrate app commands but should not duplicate business logic already owned by an app.
4. Stable human-facing documentation belongs under `docs/`.
5. Logs, temporary exports, generated receipts, local uploads, and install snapshots should stay ignored and out of git.

## Configuration Rules

- The root `package.json` is a workspace convenience manifest only.
- `frontend/package.json` is the authoritative frontend dependency manifest.
- Backend Python dependency management is owned by `backend/requirements*.txt` and `backend/pyproject.toml`.
- Local backend settings belong in `backend/.env`; local frontend settings belong in `frontend/.env`.

## Cleanup Notes

- Legacy root helper scripts, duplicate root assets, and empty legacy directories were removed during cleanup.
- Do not recreate root-level `public/`, ad hoc test scripts, or one-off install reports unless they become documented sources of truth.

## Recommended Workflow

```bash
npm run dev
```

```bash
npm run check:env
```

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## Change Review Checklist

- Is this file in the correct application or documentation directory?
- Is it a source file, or should it be generated and ignored instead?
- Does it add a second source of truth for setup, installs, or runtime behavior?
- If a new top-level path is introduced, is its ownership documented here?
