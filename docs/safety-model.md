# Safety Model

TechTools for Windows modules must be opt-in, narrow, transparent, and
reversible. A module should fail closed when it cannot prove that its current
environment matches the support evidence it requires.

## Suite Rules

- No module may claim support without repository evidence.
- No module may collect credentials, cookies, tokens, sessions, secrets, or
  unrelated personal data.
- Logging must be local unless a future module explicitly documents and
  obtains consent for another model.
- Sensitive reports must not include crash dumps, raw process memory, private
  symbols, PDB files, Microsoft binaries, full system dumps, secrets, tokens,
  private URLs, or sensitive personal data.
- Windows is referenced only as the compatibility platform.

## Taskbar ListView Boundary

Taskbar ListView has no runtime yet and no supported Windows builds. Future
hooks into private Explorer and taskbar internals are high risk because
Windows updates can change undocumented functions without notice.

Unsupported or mismatched builds must enable zero hooks, preserve native
Explorer behaviour, and avoid runtime symbol downloads.

## Browser Choice Tools Boundary

Browser Choice Tools is proposal only. Any future work must be opt-in,
transparent, reversible, and respectful of the user-selected browser and
search provider.

It must not patch Microsoft binaries, replace system files, spoof region,
disable security features, collect credentials, cookies, tokens, or sessions,
or claim that Edge is removed.
