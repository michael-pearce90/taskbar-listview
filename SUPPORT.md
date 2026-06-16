# Support

TechTools for Windows is an experimental suite. There is no implementation
runtime and the current supported-build list is **none**.

## Module Status

| Module | Status | Support |
| --- | --- | --- |
| Taskbar ListView | Documentation and research tooling only; no runtime yet | No supported Windows builds |
| Browser Choice Tools | Proposal only; no code yet | No supported runtime or behaviour |

## Taskbar ListView Build Support

Taskbar ListView may in future hook private Explorer and taskbar internals.
These interfaces are undocumented, can change in any Windows update, and
cannot be treated as compatible from a Windows release name or version range
alone.

A Windows build is supported only when its exact required module identities
and target fingerprints are recorded as validated and the complete manual
acceptance test passes on that module set.

An issue, research capture, similar version number, successful experiment, or
maintainer reply does not promise support. Unsupported builds must fail closed
and leave native Explorer behaviour unchanged.

## Browser Choice Tools Support

Browser Choice Tools has no implementation. Discussion must remain proposal
level unless a future module admission document approves implementation work.

Any future proposal must stay opt-in, transparent, reversible, local-only, and
respectful of the user's selected browser and search provider. It must not
patch Microsoft binaries, replace system files, spoof region, disable security
features, collect credentials, cookies, tokens, or sessions, or claim Edge is
removed.

## What We Can Review

- Reproducible documentation defects.
- Research captures that follow the Taskbar ListView module inventory
  checklist.
- Evidence that an exact module identity changed.
- Narrow proposals related to admitted module boundaries.

Do not paste or attach crash dumps, raw process memory, private symbols, PDB
files, Microsoft binaries, full system dumps, secrets, tokens, private URLs,
credentials, cookies, sessions, or sensitive personal data. Follow
[SECURITY.md](SECURITY.md) for security concerns.
