# Contributing to Taskbar ListView

Taskbar ListView is an experimental, standalone GPLv3 Windows 11 project. It
is not a Windhawk fork, compatibility layer, or mod host. There is no
implementation runtime and there are no supported Windows builds yet.

## Before Opening an Issue

Use the closest structured issue form. Blank issues are disabled so that
reports include enough scope and safety information to review.

Do not paste or attach crash dumps, raw process memory, private symbols, PDB
files, Microsoft binaries, full system dumps, secrets, tokens, private URLs,
or sensitive personal data.

An unsupported-build report records research evidence. It does not promise
that the build will become supported.

## Scope

Contributions should concern the compact grouped-window list shown after a
grouped taskbar click, its narrow future host, exact-build compatibility
evidence, safe rollback, or project documentation.

The following are out of scope:

- Start menu changes.
- Taskbar styling, labels, icon size, or taskbar position changes.
- Never-combine behaviour.
- Shell replacement features.
- General-purpose injection or taskbar customisation.
- Windhawk compatibility or mod hosting.

Broad taskbar customisation requests will be closed.

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

## AI-Assisted Contributions

See [docs/ai-rulebook-adoption.md](docs/ai-rulebook-adoption.md). The adoption
record is proposed on `docs/public-repo-setup`; it is not complete until
merged and checked on `main`.

The external AI Rulebook guides working behaviour and language. This
repository remains authoritative for Taskbar ListView facts, scope,
implementation truth, support state, safety boundaries, and public claims.
