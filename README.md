# TechTools for Windows

**Technician-focused open-source tools for Windows.**

TechTools for Windows is a suite repository for small, conservative Windows
tools aimed at technicians, administrators, and advanced users who need clear
scope, reversible behaviour, and honest support boundaries.

TechTools for Windows is not affiliated with or endorsed by Microsoft.
Windows is used descriptively for compatibility only. This project must not
use product logos or service marks for Microsoft, Windows, Edge, Bing,
PowerToys, or Sysinternals, and must not claim to be a Microsoft project.

Target repository slug: `techtools-for-windows`.

> [!IMPORTANT]
> **Suite status**
>
> - **Experimental:** this repository currently contains documentation,
>   research tooling, and proposals only.
> - **Runtime:** there is **no runtime yet** for any module.
> - **Supported Windows builds:** there are **no supported Windows builds**.
> - **Safety:** proposed modules that interact with private Windows internals,
>   browser-choice behaviour, or system configuration must fail closed, stay
>   opt-in, and preserve native behaviour unless support has been validated.

## Modules

| Module | Status | Summary |
| --- | --- | --- |
| [Taskbar ListView](tools/taskbar-listview/README.md) | Current experimental module | Proposed compact title list for grouped taskbar clicks. No runtime yet, no supported Windows builds, and future hooks into private Explorer/taskbar internals are high risk. |
| [Browser Choice Tools](tools/browser-choice/README.md) | Proposed future module | Proposal only. No code yet. Any future work must be opt-in, transparent, reversible, local-only, and framed as browser choice enforcement rather than Edge destruction. |

## Shared Documentation

- [Strategy](docs/strategy/techtools-for-windows.md)
- [Safety model](docs/safety-model.md)
- [Module admission](docs/module-admission.md)
- [Repository rename plan](docs/repo-rename-plan.md)
- [Funding plan](docs/funding-plan.md)
- [AI Rulebook adoption record](docs/ai-rulebook-adoption.md)
- [Third-party notices](NOTICE.md)

## Contributing

Contributions should keep the suite modular and conservative. Read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request or issue.
Do not claim implementation, validation, or support that this repository does
not demonstrate.

## Support and Security

There are no supported Windows builds and no released runtime. See
[SUPPORT.md](SUPPORT.md) for support boundaries and [SECURITY.md](SECURITY.md)
for safe reporting guidance.

Do not paste or attach crash dumps, raw process memory, private symbols, PDB
files, Microsoft binaries, full system dumps, secrets, tokens, private URLs,
credentials, cookies, sessions, or sensitive personal data.

## Licence

This project is licensed under the GNU General Public License version 3 only.
See [LICENSE](LICENSE).

Any Taskbar ListView implementation adapted from
`taskbar-thumbnails.wh.cpp` must preserve its GPLv3 status, identify the
upstream author and source, and mark modifications. MinHook is BSD-2-Clause
licensed and can be used by a GPLv3 project if its copyright and licence
notice are retained.
