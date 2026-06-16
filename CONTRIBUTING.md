# Contributing to TechTools for Windows

TechTools for Windows is an experimental GPLv3 suite for technician-focused
open-source tools for Windows. There is no implementation runtime and there
are no supported Windows builds yet.

## Before Opening an Issue

Use the closest structured issue form. Blank issues are disabled so reports
include enough scope and safety information to review.

Do not paste or attach crash dumps, raw process memory, private symbols, PDB
files, Microsoft binaries, full system dumps, secrets, tokens, private URLs,
credentials, cookies, sessions, or sensitive personal data.

An unsupported-build report records research evidence. It does not promise
that the build will become supported.

## Scope

Contributions should identify which module they affect.

Taskbar ListView contributions should concern the compact grouped-window list
shown after a grouped taskbar click, its narrow future host, exact-build
compatibility evidence, safe rollback, or module documentation.

Browser Choice Tools is proposal only. Do not add implementation code,
redirect code, installers, or runtime behaviour for that module in this PR
series.

## Pull Requests

- Keep changes focused and explain the project fact or evidence they change.
- Do not claim implementation, validation, or build support that the
  repository cannot demonstrate.
- Treat any future use of private Explorer or taskbar internals as
  experimental and liable to break after Windows updates.
- Preserve GPLv3 and third-party attribution requirements in `NOTICE.md`.
- Use plain British English in project-owned documentation.
- Run relevant checks and record what was not run.
- Complete the pull request template.

## Trademark and Affiliation

TechTools for Windows is not affiliated with or endorsed by Microsoft.
Windows is used descriptively for compatibility only.

Do not use product logos or service marks for Microsoft, Windows, Edge, Bing,
PowerToys, or Sysinternals. Do not claim this is a Microsoft project.

## AI-Assisted Contributions

See [docs/ai-rulebook-adoption.md](docs/ai-rulebook-adoption.md). The adoption
record is proposed on `docs/rename-to-techtools-for-windows`; it is not
complete until merged and checked on `main`.

The external AI Rulebook guides working behaviour and language. This
repository remains authoritative for TechTools for Windows facts, scope,
implementation truth, support state, safety boundaries, and public claims.
