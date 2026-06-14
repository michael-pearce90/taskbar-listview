# Windows Module Inventory

## Status

No Windows build has been inventoried with local evidence. No Windows build is
supported.

This document is the human-readable index for future candidate captures. The
machine-readable schema and activation rules are defined in
[offline-symbol-manifest.md](../design/offline-symbol-manifest.md).

## Inventory Scope

Each row represents one exact Windows installation after a specific servicing
state, not an entire Windows release. Record the OS build and UBR for
diagnostics, then identify compatibility by the complete module identities.

Required inventory scope:

- Windows 11 `amd64`.
- Current interactive user's `explorer.exe`.
- Native Microsoft taskbar only.
- `taskbar.dll`.
- `Taskbar.View.dll` and `ExplorerExtensions.dll`, including which are loaded
  and which owns the required XAML symbols.
- `win32u.dll` exports used by the XAML profile.
- Only the grouped-click-list hook targets.

ExplorerPatcher, StartAllBack, Start11, old-taskbar replacements, ARM64,
Windows 10, and non-Explorer shells are outside the initial inventory.

## Support Matrix

| Release bucket | Exact build/UBR | Evidence ID | Candidate profile | Acceptance | Support |
| --- | --- | --- | --- | --- | --- |
| Windows 11 23H2 | Not captured | None | Unassigned | Not run | None |
| Windows 11 24H2 | Not captured | None | Unassigned | Not run | None |
| Newer Windows 11 | Not captured | None | Unassigned | Not run | None |

The release bucket is for navigation only. A future row must contain one exact
build, one evidence bundle, and one exact set of module identities. Multiple
cumulative updates require multiple rows unless their complete module sets are
proven byte-for-byte identical and separately tested.

## Module Capture Table

Create one table per evidence ID.

| Role | Module | Loaded path | File version | PE timestamp | Image size | SHA-256 | PDB name | PDB GUID/age | Presence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shell | `explorer.exe` | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Required |
| Classic taskbar | `taskbar.dll` | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Profile-defined |
| XAML taskbar | `Taskbar.View.dll` | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Profile-defined |
| XAML taskbar alternative | `ExplorerExtensions.dll` | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Profile-defined |
| User syscall exports | `win32u.dll` | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | Not captured | XAML profile |

`Presence` becomes `required`, `allowed`, or `forbidden` in the candidate
manifest. Do not mark both XAML module names as interchangeable without
evidence from the loaded process and matching PDBs.

## Hook Target Inventory

The exact symbol spelling emitted by DIA belongs in the manifest. The shortened
names below are stable project labels for the research index.

| Target ID | Owning module | Symbol/export | Profile use | RVA | Fingerprint | ABI status |
| --- | --- | --- | --- | --- | --- | --- |
| `classic.display_extended_ui` | `taskbar.dll` | `CTaskListWnd::_DisplayExtendedUI` | Suppress non-persistent hover | Not captured | Not captured | Unreviewed |
| `classic.can_show_thumbnails` | `taskbar.dll` | `CTaskListThumbnailWnd::_CanShowThumbnails` | Force compact-list fallback | Not captured | Not captured | Unreviewed |
| `xaml.transition_sticky` | Captured XAML owner | `HoverFlyoutModel::TransitionToFlyoutVisibleStickyState` | Release delayed flyout on click | Not captured | Not captured | Unreviewed |
| `xaml.show_hover.current` | Captured XAML owner | Current `ShowTaskListButtonHoverFlyout` signature | Mark hover call/thread | Not captured | Not captured | Unreviewed |
| `xaml.show_hover.pre_kb5053656` | Captured XAML owner | Older `ShowTaskListButtonHoverFlyout` signature | Alternative hover signature | Not captured | Not captured | Unreviewed |
| `xaml.can_fit` | Captured XAML owner | `FlyoutFrame::CanFitAndUpdateScaleFactor` | Force compact-list fallback | Not captured | Not captured | Unreviewed |
| `xaml.nt_user_show_window` | `win32u.dll` | `NtUserShowWindow` | Delay hover visibility | Not captured | Not captured | Win32 export, unreviewed |
| `xaml.nt_user_enable_window` | `win32u.dll` | `NtUserEnableWindow` | Delay hover enablement | Not captured | Not captured | Win32 export, unreviewed |

Exactly one `xaml.show_hover.*` target may be selected by a profile. If neither
or both resolve unexpectedly, that candidate is unsupported pending research.

The upstream `CTaskListWnd::_ShowToolTip` target is not part of this project.
Neither are ExplorerPatcher exports, `GetWindowBand`, virtual desktop switcher
logic, or `LoadLibraryExW`.

## Calling Convention Review

Every private target requires an evidence note covering:

- Microsoft x64 ABI.
- Return type and size.
- Explicit `pThis` parameter for C++ instance methods.
- Total parameter count and width.
- Whether a parameter is by value, pointer, reference, interface wrapper, or
  WinRT value.
- Whether the function is a thunk or has an unusual entry sequence.
- Which exact upstream detour prototype was used as the starting hypothesis.
- Manual disassembly or debugger evidence that confirms the hypothesis.

The source spellings `__cdecl` and `WINAPI` do not create distinct calling
conventions on x64. They still remain useful diagnostic notes because a future
ARM64 port, x86 port, or changed prototype cannot inherit the same assumption.

## Evidence Bundle Layout

Evidence should live outside the repository while binaries and PDBs are under
Microsoft copyright. Commit only generated metadata, hashes, reports, and
review notes unless redistribution rights are established.

Recommended local bundle:

```text
evidence/<evidence-id>/
  capture.json
  modules/
    <exact copied binaries>
  pdb/
    <matching local PDBs>
  reports/
    symbols.json
    disassembly-notes.md
    module-load-order.txt
    network-isolation.txt
  candidate-manifest.json
```

The evidence ID should include the VM label and exact build/UBR without
implying support, for example
`win11-24h2-build-<build>-ubr-<ubr>-capture-01`.

## Capture Process

1. Restore a disposable VM and record its snapshot/checkpoint ID.
2. Confirm the network adapter is disconnected for the capture.
3. Record Windows edition, display version, build, UBR, channel, and
   `BuildLabEx`.
4. Confirm native `amd64` and the shell PID obtained from `GetShellWindow`.
5. Confirm the shell image is the canonical Windows `explorer.exe`.
6. Record installed shell customization software; stop if any is present.
7. Capture an initial module list.
8. Exercise grouped taskbar hover and click behavior to trigger late loads.
9. Capture the final module list and load order for the two XAML module names.
10. Copy exact relevant binaries, then record hashes and PE/CodeView identity.
11. Provide matching PDBs locally and verify GUID/age before symbol resolution.
12. Resolve only the target inventory above and record exact symbol names/RVAs.
13. Resolve `win32u.dll` exports and record their RVAs.
14. Record executable-section bounds and masked entry fingerprints.
15. Review prototypes and assign a candidate hook profile.
16. Generate deterministic `inventory-only` output.
17. Complete the manual inventory checklist and obtain reviewer sign-off.

If any required binary, PDB, symbol, export, prototype, or fingerprint cannot
be established, retain the evidence as a failed research capture and do not
create a runtime-eligible record.

## Promotion to Supported

Inventory completion alone is insufficient. Promotion requires:

1. A complete candidate profile with exact module identities and target RVAs.
2. Independent review of hashes, PDB matches, symbol resolution, fingerprints,
   and ABI notes.
3. A future runtime that consumes the manifest without symbol or network code.
4. A complete pass of `tests/manual/acceptance-test.md` on the same exact
   module set.
5. Verified disable, host-loss, Explorer restart, and uninstall rollback.
6. A no-network trace.
7. A reviewed change from `inventory-only` to `validated`.

Until all seven conditions are met, the support matrix remains `None`.

## Open Research Questions

- Which exact serviced builds use only classic, only XAML, or mixed behavior?
- Which module owns the XAML symbols on each exact build?
- Are both XAML module names ever loaded together, and if so, what presence
  rule is safe?
- Do matching public symbols exist for every target on every desired build?
- How long can the XAML module legitimately remain unloaded after shell start?
- Can a required taskbar module unload or be replaced without Explorer exit?
- What fingerprint length is stable enough to catch a wrong RVA without
  masking meaningful instructions?
- What debugger evidence is sufficient to approve each private ABI?
