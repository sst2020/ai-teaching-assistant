# 2026-04-06 Project Tidy

## Summary

Perform a repository cleanup and simplification pass so the workspace matches the active backend/frontend architecture, duplicate documentation is reduced, generated artifacts are removed, and configuration surfaces are easier to reason about.

## Goal

Reduce repository ambiguity and stale root clutter while preserving live backend and frontend behavior.

## Deliverable

- Updated repository guide and structure documentation.
- Consolidated setup and roadmap documentation.
- Removed redundant legacy files, reports, scripts, and empty root directories that are no longer part of the active workspace.
- Updated environment templates, ignore rules, and dependency manifests.
- Governed runtime artifacts for this `vibe` run.

## Constraints

- Do not modify active backend/frontend application behavior except for manifest or template cleanup.
- Do not revert or overwrite existing user changes in the dirty worktree.
- Keep deletions limited to files and directories shown to be duplicate, generated, or unreferenced by the active workflow.

## Acceptance Criteria

- Root README reflects the current workspace and documentation layout.
- `docs/DEVELOPMENT_SETUP.md` becomes the single setup/debugging guide.
- TODO documentation is clearly separated by language under `docs/`.
- Empty root legacy directories and obsolete root helper scripts are removed.
- `.gitignore` and subdirectory ignore files cover local-only and generated artifacts.
- Dependency manifests remove clearly unused packages and remain internally consistent.
- New governed requirement/plan artifacts exist for traceability.

> Fill the anti-drift fields once here. Downstream governed plan and completion surfaces should reuse them rather than restate them.

## Primary Objective

Improve repository navigability, documentation clarity, and configuration hygiene without changing product functionality.

## Non-Objective Proxy Signals

- Deleting active source files instead of only redundant or generated files.
- Replacing multiple docs with weaker documentation.
- Claiming dependency correctness without verifying usage via repo search.

## Validation Material Role

Repository files, `git status`, search results, and manifests are validation inputs only. They justify cleanup only when they show a file is redundant, generated, or outside the active workspace model.

## Anti-Proxy-Goal-Drift Tier

Brownfield cleanup with documentation consolidation, root-structure cleanup, and conservative manifest hygiene.

## Intended Scope

Root docs, workspace manifests, env templates, ignore rules, governed artifacts, and redundant root/backend artifacts shown to be stale.

## Abstraction Layer Target

Repository organization, developer workflow surface, and local configuration surface.

## Completion State

Cleanup complete, with duplicate docs reduced, stale root artifacts removed, and workspace ownership made explicit.

## Generalization Evidence Bundle

- Updated README, setup guide, structure guide, and TODO index.
- Updated env templates and dependency manifests.
- Search evidence showing removed files were unreferenced by the active workspace flow.
- Verification that manifest files remain readable and the diff stays within the declared scope.

## Non-Goals

- Refactoring backend or frontend feature logic.
- Moving code between `backend/` and `frontend/`.
- Guaranteeing every remaining doc is historically up to date beyond the cleaned scope.

## Autonomy Mode

Interactive governed with inferred assumptions and no extra confirmation because the requested cleanup is repo-local and evidence-based.

## Assumptions

- “Comprehensive cleanup and simplification” includes removing stale root scripts and generated reports when searches show they are no longer referenced.
- Existing uncommitted changes outside this scope belong to the user and must remain untouched.
- `temp/` and runtime receipts are local working artifacts rather than canonical project content.

## Evidence Inputs

- Repository root listing and current `git status --short`.
- Search results for legacy root scripts, duplicate docs, env usage, and dependency usage.
- Existing `README.md`, `.gitignore`, `package.json`, `frontend/package.json`, `backend/requirements*.txt`, and env templates.
