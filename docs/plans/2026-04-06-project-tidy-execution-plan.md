# 2026-04-06 Project Tidy Execution Plan

## Execution Summary

Execute a serial repository cleanup pass focused on documentation consolidation, root-level simplification, conservative dependency cleanup, and generated-artifact hygiene.

## Frozen Inputs

- Requirement doc: `docs/requirements/2026-04-06-project-tidy.md`
- Current dirty worktree must be preserved.

## Anti-Proxy-Goal-Drift Controls

Prefill from the frozen requirement doc where available. Only diverge with explicit justification.

### Primary Objective

Improve repository navigability, documentation clarity, and configuration hygiene without changing product functionality.

### Non-Objective Proxy Signals

- Removing active source files.
- Treating historical reports or install snapshots as authoritative docs.
- Removing dependencies without confirming lack of usage through search.

### Validation Material Role

Use repo files, searches, and command output to verify cleanup candidates; do not infer permission for structural migration from them.

### Declared Tier

Brownfield cleanup.

### Intended Scope

README, setup doc, structure doc, TODO docs, env templates, dependency manifests, ignore rules, governed artifacts, and redundant repo-local files proven stale.

### Abstraction Layer Target

Repository organization, workflow surface, and local configuration surface.

### Completion State Target

Workspace docs are consolidated, redundant root artifacts are removed, dependency manifests are cleaned conservatively, and no product logic changed.

### Generalization Evidence Plan

- Inspect the resulting diff.
- Confirm the root and frontend manifests remain readable JSON.
- Confirm moved TODO docs and setup docs exist under `docs/`.
- Confirm removed files are no longer referenced by root docs.

## Internal Grade Decision

`L`

Reason: the task spans multiple artifacts and some removals, but it does not justify XL parallel execution or application-level refactoring.

## Wave Plan

### Wave 1

- Refresh governed runtime artifacts for skeleton and intent.
- Freeze requirement and plan documents against the actual cleanup scope.

### Wave 2

- Remove stale root scripts, duplicate root assets, generated reports, and empty root legacy directories.
- Move TODO docs under `docs/`.
- Consolidate setup/debug/install guidance into `docs/DEVELOPMENT_SETUP.md`.
- Rewrite root `README.md` and `docs/REPOSITORY_STRUCTURE.md`.
- Update `.gitignore`, env templates, and dependency manifests.

### Wave 3

- Run targeted verification commands and searches.
- Write execution and cleanup receipts.

## Ownership Boundaries

- Root-governed lane only.
- Write scope: repository docs, workspace manifests, env templates, ignore files, and redundant files explicitly removed by this cleanup.
- No subagents.

## Verification Commands

```powershell
node -p "Object.keys(require('./package.json').scripts).join(', ')"
node -p "require('./frontend/package.json').dependencies['axios']"
git diff --stat
git status --short
rg -n "DEBUGGING_GUIDE|TODO_zh-CN|TODO\.md" README.md docs backend frontend
```

## Rollback Plan

- Revert only the files in the declared write scope if this cleanup needs to be undone.
- Do not revert unrelated dirty files already present before this task.

## Phase Cleanup Contract

- Record verification results in a phase receipt.
- Record which stale files were removed or consolidated.
- Leave runtime receipts under `outputs/runtime/`.
- Downgrade completion language if verification fails or if any scope drift occurs.
