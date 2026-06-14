# AI Rulebook Adoption

## Adoption Record

- **Adoption state:** Proposed on branch `docs/public-repo-setup`.
- **Baseline:** `michael-pearce90/ai-rulebook` `main`, checked 2026-06-14.
- **Scope:** AI working rules, language rules, source discipline, and GitHub
  destination text.
- **Local adapters:** Windows shell safety; Explorer and taskbar internals; no
  sensitive dumps; no support claims without validated build evidence.
- **Conflicts found:** None known from current checks.
- **Excluded:** Parity, cleanup, archive, and delete readiness.

This is a local adoption record, not a copy of the AI Rulebook. Taskbar
ListView remains the source of truth for project facts, scope, implementation
truth, support state, safety boundaries, and public claims.

Where general guidance and this repository differ on a project fact or safety
boundary, follow this repository. Changes to the external Rulebook do not
silently change this project's recorded position; they require a fresh review
and an explicit local update.

Adoption is not complete unless and until this record is merged and checked on
the Taskbar ListView `main` branch. While it exists only on
`docs/public-repo-setup`, it must be described as proposed.

## Project Adapters

AI-assisted work in this repository must:

- use plain British English for project-owned public wording;
- distinguish research, proposals, candidate evidence, validated evidence, and
  implemented behaviour;
- treat private Explorer and taskbar internals as unstable and high risk;
- avoid destructive or broadly targeted Windows shell commands;
- never request or publish crash dumps, raw process memory, private symbols,
  PDB files, Microsoft binaries, full system dumps, secrets, tokens, private
  URLs, or sensitive personal data;
- make no Windows build support claim without exact validated module evidence
  and the required acceptance-test results;
- state that unsupported or mismatched builds must fail closed; and
- keep GitHub issue and pull request destinations within the
  `taskbar-listview` repository rather than the AI Rulebook repository.
