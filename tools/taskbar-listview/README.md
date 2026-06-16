# Taskbar ListView

Taskbar ListView is the first current experimental module in TechTools for
Windows.

It is a one-purpose experiment: when a grouped taskbar icon is clicked, show a
compact vertical list of readable window titles instead of wide thumbnail
previews.

> [!IMPORTANT]
> **Module status**
>
> - **Experimental:** documentation and research tooling only.
> - **Support:** there are **no supported Windows builds**.
> - **Runtime:** there is **no runtime yet**. There is no injector, DLL, hook
>   implementation, installer, or packaged release.
> - **Compatibility risk:** a future implementation may rely on private
>   Explorer and taskbar internals that can break after Windows updates.

The module records research and a proposed narrow design. It does not provide
working taskbar software.

## Purpose

The intended behaviour is deliberately small:

- A grouped taskbar click would open the native compact title list.
- Window titles would remain readable without wide thumbnail cards.
- Hover would not open the grouped-window preview.
- Any future unsupported or mismatched build would fail closed and preserve
  native Explorer behaviour.

The proposed implementation is informed by Michael Maltsev's Windhawk mod,
[Disable Taskbar Thumbnails][upstream-mod]. Taskbar ListView is independent:
it is not a Windhawk fork, compatibility layer, or general Windows
customisation host.

## Non-Goals

- General taskbar customisation or shell replacement.
- Start menu changes.
- Taskbar styling, labels, icon size, position, theming, or never-combine
  behaviour.
- ExplorerPatcher or old Windows 10 taskbar compatibility.
- Windhawk compatibility, mod hosting, or embedding the Windhawk runtime.
- General-purpose mod loading or arbitrary process injection.
- A service, driver, updater, telemetry, or remote control.
- Claiming support from a Windows version number, research capture, or
  unvalidated test.

## Research Status

The research spike concluded that the concept appears feasible only with
strict exact-build gating. The current design proposes:

- targeting only the current interactive user's shell `explorer.exe`;
- limiting any future host to Windows 11 on x64;
- using one narrowly scoped x64 DLL;
- using MinHook, or an equivalently small detour library, for hook
  installation and removal;
- resolving private taskbar functions from an offline manifest keyed by exact
  module identity, without runtime symbol downloads; and
- refusing to install hooks unless the running modules exactly match a tested
  manifest entry.

These are design proposals, not implemented behaviour. See
[the extraction research](docs/research/windhawk-mod-extraction.md),
[the proposed host design](docs/design/minimal-standalone-host.md), and
[the offline symbol manifest design](docs/design/offline-symbol-manifest.md).

## Safety Boundary

A future implementation would hook private, undocumented Explorer and taskbar
internals. Windows updates can rename functions, change calling conventions,
remove code, or alter behaviour without notice. A bad hook can crash or
restart Explorer.

An unrecognised Windows or module build must be treated as unsupported. A
version number range alone is not sufficient evidence of compatibility.
Unsupported builds must fail closed and preserve native Explorer behaviour.

## Module Documentation

- [Windhawk mod extraction research](docs/research/windhawk-mod-extraction.md)
- [Windows module inventory](docs/research/windows-module-inventory.md)
- [Minimal standalone host design](docs/design/minimal-standalone-host.md)
- [Offline symbol manifest design](docs/design/offline-symbol-manifest.md)
- [Manual acceptance test](tests/manual/acceptance-test.md)
- [Module inventory checklist](tests/manual/module-inventory-checklist.md)
- [Public repository presentation note](docs/design/public-repo-presentation.md)
- [Symbol manifest tool](symbol-manifest/README.md)

## Licence and Attribution

Taskbar ListView is part of a GPLv3-only suite. Any implementation adapted
from `taskbar-thumbnails.wh.cpp` must preserve its GPLv3 status, identify the
upstream author and source, and mark modifications. See
[the suite notices](../../NOTICE.md).

[upstream-mod]: https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp
