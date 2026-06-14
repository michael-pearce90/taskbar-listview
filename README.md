# Taskbar Click List

Research spike for a small Windows 11 tool that changes one taskbar behavior:
clicking a grouped taskbar button should show a compact text list instead of
thumbnail previews.

The proposed implementation adapts only the relevant behavior from Michael
Maltsev's Windhawk mod, [Disable Taskbar Thumbnails][upstream-mod]. It is not a
Windhawk fork and is not intended to become a general Windows customization
host.

## Status

Documentation only. There is no injector, DLL, hook implementation, installer,
or supported Windows build yet.

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
or alter behavior without notice. A bad hook can crash or restart Explorer.

An unrecognized Windows or module build must be treated as unsupported. A
version number range alone is not sufficient evidence of compatibility.

## Intended Scope

- Windows 11, x64 only.
- Current interactive user's shell `explorer.exe` only.
- Grouped taskbar click opens the native compact list.
- Hover does not open the grouped-window preview.
- Local enable, disable, status, and clean uninstall behavior.
- No runtime network access.

## Non-Goals

- Forking or embedding the Windhawk runtime.
- General-purpose mod loading or arbitrary process injection.
- Start menu changes, taskbar styling, labels, icon size, position, theming, or
  never-combine behavior.
- ExplorerPatcher or old Windows 10 taskbar compatibility.
- A service, driver, updater, telemetry, or remote control.
- Claiming support for builds that have not passed the manual acceptance test.

## Documentation

- [Windhawk mod extraction research](docs/research/windhawk-mod-extraction.md)
- [Minimal standalone host design](docs/design/minimal-standalone-host.md)
- [Manual acceptance test](tests/manual/acceptance-test.md)
- [Third-party notices](NOTICE.md)

## License

This project is licensed under the GNU General Public License version 3 only.
See [LICENSE](LICENSE).

Any implementation adapted from `taskbar-thumbnails.wh.cpp` must preserve its
GPLv3 status, identify the upstream author and source, and mark modifications.
MinHook is BSD-2-Clause licensed and can be used by a GPLv3 project if its
copyright and license notice are retained.

[upstream-mod]: https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp
