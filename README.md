# Taskbar ListView

Taskbar ListView is an experimental Windows 11 tool for showing a compact list
of window titles when clicking grouped taskbar icons instead of wide
thumbnails.

The proposed implementation adapts only the relevant behaviour from Michael
Maltsev's Windhawk mod, [Disable Taskbar Thumbnails][upstream-mod]. It is not a
Windhawk fork and is not intended to become a general Windows customisation
host.

## Status

Documentation and research tooling only. There is no implementation runtime,
injector, DLL, hook implementation, installer, or supported Windows build yet.

The spike verdict is **feasible with strict build gating**:

- Use a per-user launcher that targets only the current shell's `explorer.exe`.
- Inject one x64 DLL into that process.
- Use MinHook, or an equivalently small detour library, for hook installation
  and removal.
- Resolve private taskbar functions from an offline manifest keyed by exact
  module identity. The runtime must not download symbols.
- Refuse to install hooks when the running modules do not exactly match a
  tested manifest entry.

See [the extraction research](docs/research/windhawk-mod-extraction.md) and
[the proposed host design](docs/design/minimal-standalone-host.md).

## Safety Warning

This project would hook private, undocumented Explorer and taskbar internals.
Windows updates can rename functions, change calling conventions, remove code,
or alter behaviour without notice. A bad hook can crash or restart Explorer.

An unrecognised Windows or module build must be treated as unsupported. A
version number range alone is not sufficient evidence of compatibility.
Unsupported builds must fail closed and preserve native Explorer behaviour.

## Intended Scope

- Windows 11, x64 only.
- Current interactive user's shell `explorer.exe` only.
- A grouped taskbar click opens the native compact list.
- Hover does not open the grouped-window preview.
- Local enable, disable, status, and clean uninstall behaviour.
- No runtime network access.

## Non-Goals

- Forking or embedding the Windhawk runtime.
- General-purpose mod loading or arbitrary process injection.
- Start menu changes, taskbar styling, labels, icon size, position, theming, or
  never-combine behaviour.
- ExplorerPatcher or old Windows 10 taskbar compatibility.
- A service, driver, updater, telemetry, or remote control.
- Claiming support for builds that have not passed the manual acceptance test.
- Broad taskbar customisation or shell replacement features.
- Windhawk compatibility or mod hosting.

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
- [Manual acceptance test](tests/manual/acceptance-test.md)
- [AI Rulebook adoption record](docs/ai-rulebook-adoption.md)
- [Third-party notices](NOTICE.md)

## License

This project is licensed under the GNU General Public License version 3 only.
See [LICENSE](LICENSE).

Any implementation adapted from `taskbar-thumbnails.wh.cpp` must preserve its
GPLv3 status, identify the upstream author and source, and mark modifications.
MinHook is BSD-2-Clause licensed and can be used by a GPLv3 project if its
copyright and license notice are retained.

[upstream-mod]: https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp
