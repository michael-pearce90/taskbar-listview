# Module Inventory Checklist

## Purpose

Use this checklist to capture one exact Windows 11 module set and generate an
`inventory-only` symbol-manifest candidate.

Completing this checklist does not make a build supported. Support requires a
future implementation and a full pass of
[acceptance-test.md](acceptance-test.md) on the same exact module set.

## Tool Test Preflight

- [ ] `python -B -m unittest discover` passes from the repository root.
- [ ] Successful inventory is verified manually on Windows using a copied
      local AMD64 PE file with readable file and product version metadata.
- [ ] The copied PE, any PDB, and generated real-module inventory remain
      outside the repository.

## Evidence Header

- Evidence ID:
- Capture date/time UTC:
- Operator:
- Reviewer:
- Repository commit:
- Generator version/commit:
- VM name:
- VM snapshot/checkpoint:
- Windows release label:
- Edition:
- Display version:
- Build:
- UBR:
- `BuildLabEx`:
- Release channel:
- Architecture:

## Isolation and Preconditions

- [ ] The machine is a disposable VM or otherwise recoverable test system.
- [ ] The VM snapshot/checkpoint is recorded.
- [ ] The intended Windows servicing state was completed before capture.
- [ ] The virtual network adapter is disconnected for capture and resolution.
- [ ] No Microsoft symbol server, Windhawk cache, or other network fallback is
      configured.
- [ ] The current shell PID was obtained from `GetShellWindow`, not process
      name enumeration.
- [ ] The shell process belongs to the current interactive user and session.
- [ ] The shell image resolves to the canonical Windows `explorer.exe`.
- [ ] The OS and shell are native `amd64`.
- [ ] Windhawk and all taskbar mods are disabled.
- [ ] ExplorerPatcher, StartAllBack, Start11, and similar shell replacements
      are absent.
- [ ] Baseline grouped taskbar hover and click behavior is recorded.

Stop the capture if any scope or isolation check fails.

## OS Evidence

- [ ] Product name and edition are captured.
- [ ] Display version is captured.
- [ ] Build and UBR are captured separately.
- [ ] `BuildLabEx` is captured.
- [ ] Installation type and release channel are captured.
- [ ] Installed cumulative update identifiers are recorded.
- [ ] System architecture is captured with a native-architecture API.
- [ ] OS metadata is treated as diagnostic, not as the manifest match key.

## Module Load Observation

Capture module state before and after exercising a grouped taskbar item.

- [ ] Initial `explorer.exe` loaded-module list is saved.
- [ ] Native grouped taskbar hover is exercised.
- [ ] Native grouped taskbar click is exercised.
- [ ] Final loaded-module list is saved.
- [ ] Module load order relevant to `Taskbar.View.dll` and
      `ExplorerExtensions.dll` is recorded.
- [ ] The exact loaded path for every relevant module is recorded.
- [ ] It is recorded whether `Taskbar.View.dll` is absent or present.
- [ ] It is recorded whether `ExplorerExtensions.dll` is absent or present.
- [ ] If both are present, the symbol-owning module and role of the other
      module are investigated rather than assumed.
- [ ] A proposed `required`, `allowed`, or `forbidden` presence rule is
      recorded for each relevant module.

## Module Identity

Complete these checks for `explorer.exe`, `taskbar.dll`, the observed XAML
module or modules, and `win32u.dll`.

- [ ] Lowercase module base name is captured.
- [ ] Canonical path relative to `%SystemRoot%` is captured.
- [ ] PE machine is `amd64`.
- [ ] File version is captured.
- [ ] Product version is captured.
- [ ] PE `TimeDateStamp` is captured in hexadecimal.
- [ ] PE `SizeOfImage` is captured.
- [ ] SHA-256 of the exact copied image is captured.
- [ ] Authenticode verification result is recorded.
- [ ] CodeView PDB name is captured.
- [ ] CodeView GUID and age are captured.
- [ ] The copied image hash is rechecked before symbol resolution.
- [ ] No system binary was modified, replaced, or patched during capture.

Record missing debug information explicitly. Do not substitute a version
number for absent CodeView identity.

## Local PDB Verification

For every private-symbol module:

- [ ] The PDB is present on local controlled media or in the evidence bundle.
- [ ] The PDB path is absolute and local.
- [ ] The binary CodeView PDB name matches the selected PDB.
- [ ] The binary CodeView GUID matches the selected PDB.
- [ ] The binary CodeView age matches the selected PDB.
- [ ] DIA is configured for the explicit local PDB.
- [ ] Symbol-server and original-path fallback access are disabled.
- [ ] Resolution succeeds while the VM has no network adapter.

If any PDB is missing or mismatched, mark the candidate failed and stop before
profile assignment.

## Private Symbol Resolution

### Classic Targets

- [ ] `CTaskListWnd::_DisplayExtendedUI` is resolved or explicitly absent.
- [ ] `CTaskListThumbnailWnd::_CanShowThumbnails` is resolved or explicitly
      absent.
- [ ] The exact DIA symbol spelling is recorded for every resolved target.
- [ ] The upstream tooltip target is excluded.

### XAML Targets

- [ ] `HoverFlyoutModel::TransitionToFlyoutVisibleStickyState` is resolved or
      explicitly absent.
- [ ] The current `ShowTaskListButtonHoverFlyout` signature is resolved or
      explicitly absent.
- [ ] The pre-KB5053656 `ShowTaskListButtonHoverFlyout` signature is resolved
      or explicitly absent.
- [ ] Exactly one known hover signature is selected, or the candidate is
      marked failed for investigation.
- [ ] `FlyoutFrame::CanFitAndUpdateScaleFactor` is resolved or explicitly
      absent.
- [ ] The exact owning module is recorded for every XAML symbol.
- [ ] Exact DIA symbol spellings are recorded.

### Export Targets

- [ ] `win32u.dll!NtUserShowWindow` resolves.
- [ ] `win32u.dll!NtUserEnableWindow` resolves.
- [ ] Export RVAs are recorded.
- [ ] Forwarded or unexpected export resolution is rejected.

## RVA and Fingerprint Review

For every selected target:

- [ ] The RVA is calculated from the exact image base.
- [ ] The RVA is less than `SizeOfImage`.
- [ ] The complete fingerprint range is inside the image.
- [ ] The target and fingerprint are inside an executable section.
- [ ] Fingerprint bytes contain complete x64 instructions.
- [ ] The fingerprint mask is not all zero.
- [ ] Every masked byte has a written rationale.
- [ ] Disassembly is saved with the evidence report.
- [ ] Obvious import thunks, jump stubs, aliases, and duplicate addresses are
      investigated.
- [ ] A second generation run produces the same RVA and fingerprint.

## ABI and Prototype Review

For every private target:

- [ ] Microsoft x64 ABI is recorded.
- [ ] Return type and width are recorded.
- [ ] The explicit `pThis` parameter is recorded for instance methods.
- [ ] Parameter count, order, and width are recorded.
- [ ] Pointer, reference, interface, and WinRT value semantics are recorded.
- [ ] The corresponding pinned upstream prototype is cited.
- [ ] Disassembly or debugger evidence supports the proposed prototype.
- [ ] The record states that source `__cdecl`/`WINAPI` spelling does not
      distinguish x64 calling convention.
- [ ] A project `prototype_id` is assigned.
- [ ] Reviewer approves the ABI note for this exact module identity.

An unresolved ABI question keeps the candidate unsupported even if the symbol
and fingerprint match.

## Profile Assignment

- [ ] The profile name describes behavior and ABI revision, not only `23H2` or
      `24H2`.
- [ ] The profile behavior is exactly `grouped-click-list`.
- [ ] Every required module ID is listed.
- [ ] Required, allowed, and forbidden module presence is explicit.
- [ ] Every required target is listed.
- [ ] The hover signature is represented as an `exactly_one` requirement.
- [ ] Classic, XAML, or mixed selection is justified by local evidence.
- [ ] Missing targets are not made optional to force a profile match.
- [ ] Tooltip, virtual desktop, ExplorerPatcher, and broad taskbar targets are
      absent.
- [ ] The transaction policy requires one all-or-nothing enable.
- [ ] Late-module policy requires zero hooks while waiting.
- [ ] Required-module unload/reload requires complete profile disable.

## Candidate Output

- [ ] `schema_version` is recognized.
- [ ] `support_state` is `inventory-only`.
- [ ] `support_note` says acceptance has not established support.
- [ ] Generator and upstream source revisions are recorded.
- [ ] All module and target IDs are unique.
- [ ] All required schema fields are present.
- [ ] No absolute maintainer-machine path appears in committed output.
- [ ] No Microsoft binary or PDB is added to the repository.
- [ ] A clean second run is byte-for-byte identical.
- [ ] Schema verification exits successfully.
- [ ] Release compilation rejects the `inventory-only` record.

## Network Verification

During capture and resolution:

- [ ] The VM network adapter remains disconnected.
- [ ] No DNS request occurs.
- [ ] No HTTP or HTTPS connection occurs.
- [ ] No Microsoft symbol-server request occurs.
- [ ] No Windhawk cache request occurs.
- [ ] No updater, telemetry, or package-manager request occurs.
- [ ] The evidence report records how isolation was verified.

## Review and Disposition

- [ ] Operator signs the evidence report.
- [ ] Reviewer independently checks module identities and PDB matches.
- [ ] Reviewer independently checks target RVAs and fingerprints.
- [ ] Reviewer checks profile completeness and late-module policy.
- [ ] Open questions and deviations are listed.
- [ ] Candidate is added to the research inventory as unsupported.
- [ ] No README, release note, UI, or package claims build support.

Disposition:

- [ ] Failed capture; insufficient or inconsistent evidence.
- [ ] Complete inventory candidate; still unsupported.
- [ ] Rejected as out of scope.

There is intentionally no "supported" disposition in this checklist.
