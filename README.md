# Taskbar ListView

**List view for grouped Windows 11 taskbar clicks.**

Taskbar ListView is a one-purpose experiment: when a grouped taskbar icon is
clicked, show a compact vertical list of readable window titles instead of
wide thumbnail previews.

> [!IMPORTANT]
> **Project status**
>
> - **Experimental:** documentation and research tooling only.
> - **Support:** there are **no supported Windows builds**.
> - **Runtime:** there is **no runtime yet**. There is no injector, DLL, hook
>   implementation, installer, or packaged release.
> - **Compatibility risk:** a future implementation may rely on private
>   Explorer and taskbar internals that can break after Windows updates.

The repository records research and a proposed narrow design. It does not
provide working taskbar software.

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

## Support

Current supported Windows builds: **none**.

An issue report, research capture, or matching Windows version does not create
a support promise. Support can be claimed only for an exact module set with
validated build evidence and a complete acceptance-test pass.

See [SUPPORT.md](SUPPORT.md) for the support boundary and
[SECURITY.md](SECURITY.md) for safe reporting guidance.

## Contributing

Contributions should stay within the one-purpose grouped-click list scope.
Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request or issue.
The structured issue forms reject broad taskbar customisation requests.

## AI Working Rules

This branch proposes adopting selected working and language rules from
`michael-pearce90/ai-rulebook`. The project repository remains authoritative
for project facts, scope, implementation truth, support state, safety
boundaries, and public claims.

Adoption is not complete unless and until the adoption record is merged and
checked on this repository's `main` branch. See
[docs/ai-rulebook-adoption.md](docs/ai-rulebook-adoption.md).

## Documentation

- [Windhawk mod extraction research](docs/research/windhawk-mod-extraction.md)
- [Minimal standalone host design](docs/design/minimal-standalone-host.md)
- [Offline symbol manifest design](docs/design/offline-symbol-manifest.md)
- [Manual acceptance test](tests/manual/acceptance-test.md)
- [Public repository presentation](docs/design/public-repo-presentation.md)
- [AI Rulebook adoption record](docs/ai-rulebook-adoption.md)
- [Third-party notices](NOTICE.md)

## Licence

This project is licensed under the GNU General Public License version 3 only.
See [LICENSE](LICENSE).

Any implementation adapted from `taskbar-thumbnails.wh.cpp` must preserve its
GPLv3 status, identify the upstream author and source, and mark modifications.
MinHook is BSD-2-Clause licensed and can be used by a GPLv3 project if its
copyright and licence notice are retained.

[upstream-mod]: https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp
