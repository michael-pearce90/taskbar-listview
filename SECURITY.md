# Security Policy

## Project State

Taskbar ListView is experimental. There is no implementation runtime and no
supported Windows build yet.

A future implementation would hook private, undocumented Explorer and taskbar
internals. Windows updates may break those internals. Unknown, changed, or
partially matched builds must fail closed without installing hooks.

## Reporting a Security Concern

Do not include sensitive evidence in a public issue or pull request.
In particular, do not paste or attach:

- crash dumps;
- raw process memory;
- private symbols;
- PDB files;
- Microsoft binaries;
- full system dumps;
- secrets;
- tokens;
- private URLs; or
- sensitive personal data.

If GitHub private vulnerability reporting is enabled for the future public
repository, use it. It is not enabled by this branch. Otherwise, open a
minimal security issue containing no sensitive details and ask the maintainer
for a private contact route.

State only the affected project document or future release, the general impact,
and whether public discussion would expose sensitive material.

## Supported Versions

There are no supported versions or Windows builds. Documentation and research
material may still receive security corrections, but that is not a runtime
support commitment.

This policy does not authorise testing against systems, accounts, or software
you do not own or have explicit permission to test.
