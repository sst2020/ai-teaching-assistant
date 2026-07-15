# AI Teaching Assistant

AI Teaching Assistant is a FastAPI + Vue 3 workspace. The live application code is split between `backend/` and `frontend/`; the repository root is reserved for shared documentation, lightweight orchestration, and workspace-level config.

## Workspace Entry Points

```bash
# Start backend + frontend from the repo root
npm run dev

# Validate local prerequisites and folder layout
npm run check:env

# Frontend commands from the repo root
npm run frontend:start
npm run frontend:build
npm run frontend:test
```

You can still work inside each app directly:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000

cd ../frontend
npm run dev
```

## Project Layout

```text
.
├── backend/                  FastAPI API, models, services, migrations, tests
├── frontend/                 Vue 3 application
├── docs/                     Stable project documentation and governed artifacts
├── issues/                   Product and backlog notes
├── scripts/                  Root-level workspace helpers
├── temp/                     Local scratch space, ignored
└── outputs/runtime/          Local runtime receipts, ignored
```

See [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md) for placement rules and ownership boundaries.

## Environment Files

- `backend/.env.example`: authoritative backend template for local development.
- `frontend/.env.example`: authoritative frontend template for local development.
- `.env.development`, `.env.staging`, `.env.production`: root-level deployment or compose presets, not replacements for `backend/.env`.

## Common Docs

- [Development Setup](docs/DEVELOPMENT_SETUP.md)
- [Repository Structure](docs/REPOSITORY_STRUCTURE.md)
- [System Testing Report](docs/SYSTEM_TESTING_REPORT.md)
- [User Interface Guide](docs/USER_INTERFACE_GUIDE.md)
- [TODO Index](docs/TODO.md)

## Maintenance Rules

- Keep new product code under `backend/` or `frontend/`.
- Keep root scripts thin; they should orchestrate existing app commands rather than duplicate app logic.
- Keep generated files, caches, logs, scratch directories, and runtime receipts out of git.
- Prefer one authoritative document per topic instead of parallel setup, install, and debugging guides.

## License

MIT. See [LICENSE](LICENSE).
