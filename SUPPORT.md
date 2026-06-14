# Support

Taskbar ListView is an experimental Windows 11 tool project. There is no
implementation runtime and the current supported-build list is **none**.

The project may in future hook private Explorer and taskbar internals. These
interfaces are undocumented, can change in any Windows update, and cannot be
treated as compatible from a Windows release name or version range alone.

## Build Support

A Windows build is supported only when its exact required module identities
and target fingerprints are recorded as validated and the complete manual
acceptance test passes on that module set.

An issue, research capture, similar version number, successful experiment, or
maintainer reply does not promise support. Unsupported builds must fail closed
and leave native Explorer behaviour unchanged.

## What We Can Review

- Reproducible documentation defects.
- Research captures that follow the module inventory checklist.
- Evidence that an exact module identity changed.
- Narrow proposals related to grouped taskbar click list behaviour.

## What Is Out of Scope

- Start menu changes.
- Taskbar styling, labels, icon size, or taskbar position changes.
- Never-combine behaviour.
- Shell replacement features.
- General Windows repair or taskbar troubleshooting.
- Windhawk compatibility or mod hosting.

Do not paste or attach crash dumps, raw process memory, private symbols, PDB
files, Microsoft binaries, full system dumps, secrets, tokens, private URLs,
or sensitive personal data. Follow [SECURITY.md](SECURITY.md) for security
concerns.
