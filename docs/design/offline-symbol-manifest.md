# Offline Symbol Manifest Design

## Status

Design only. There is no manifest generator, runtime consumer, injector, hook
implementation, or supported Windows build.

The repository support set remains **none**. An inventory record is evidence
for research; it is not a support claim and must not be accepted by a future
runtime.

## Purpose

The standalone tool needs addresses for undocumented taskbar functions without
performing symbol lookup or network access inside `explorer.exe`. The offline
symbol manifest is the reviewed boundary between:

- a maintainer environment that has exact Windows binaries and matching PDBs;
- a test VM that inventories and validates one exact Windows installation; and
- an end-user runtime that can only compare local modules with an allowlist and
  calculate `module base + RVA`.

The manifest is not a compatibility heuristic. It is an allowlist of complete,
tested module sets and hook profiles.

## Design Principles

- Windows 11 and `amd64` only.
- Target only the current interactive user's shell `explorer.exe`.
- Use exact module identity, not a Windows release label or version range.
- Record every hook address as an RVA, including exported `win32u.dll`
  functions.
- Require a complete profile before enabling any hook.
- Keep candidate inventory distinct from runtime-supported data.
- Perform no DbgHelp, DIA, PDB, symbol-server, HTTP, DNS, or update work at
  runtime.
- Fail closed on malformed, unknown, ambiguous, incomplete, or mismatched
  data.
- Preserve enough provenance to reproduce and audit every generated record.

## Manifest Artifacts

The future tooling should produce two logically separate artifacts.

### Candidate Inventory

A candidate record contains captured module identities, resolved symbols,
RVAs, fingerprints, and review notes. Its `support_state` is
`inventory-only`. Candidate records may be committed for research and must
never activate hooks.

### Release Manifest

A release manifest contains only records whose `support_state` is `validated`.
A record can become validated only after the complete behavior, rollback,
restart, uninstall, and no-network acceptance suite passes on the exact module
set.

The release build should transform reviewed source data into a deterministic,
read-only runtime representation. The runtime must also check
`support_state == "validated"`; omission from a release manifest is not the
only protection against accidental activation.

## Proposed Schema

JSON is proposed for reviewed source data because it is portable, diffable,
and supported by strict parsers. A future build may compile it into a binary
table, but the generated table must preserve the same fields and semantics.

Unknown fields should be rejected unless a later schema version explicitly
defines forward-compatible extension points. Duplicate IDs, duplicate module
roles, duplicate target IDs, and duplicate build keys are invalid.

### Top-Level Record

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | Yes | Exact parser contract, initially `1` |
| `manifest_id` | Yes | Stable release or candidate-set identifier |
| `generated_at_utc` | Yes | ISO 8601 generation time |
| `generator` | Yes | Tool name, version, and source commit |
| `source_revisions` | Yes | Reviewed upstream mod, Windhawk, and MinHook revisions |
| `build_records` | Yes | Array of exact Windows/module-set records |

### Build Record

| Field | Required | Meaning |
| --- | --- | --- |
| `build_record_id` | Yes | Stable identifier for this exact evidence set |
| `support_state` | Yes | `inventory-only`, `validated`, or `retired` |
| `support_note` | Yes | Human-readable reason for the current state |
| `windows_release_label` | Yes | Diagnostic label such as `23H2` or `24H2`; never a key |
| `os_identity` | Yes | Product name, edition, build, UBR, display version, and channel |
| `architecture` | Yes | Must be `amd64` |
| `shell_scope` | Yes | Must be `explorer-only` |
| `hook_profile_name` | Yes | Complete profile selected for this module set |
| `modules` | Yes | Exact required, allowed, and forbidden module observations |
| `hook_profiles` | Yes | Profile requirements and target alternatives |
| `evidence` | Yes | VM, capture, review, and acceptance provenance |

`os_identity` is diagnostic and helps reproduce the VM. Runtime selection is
still based on the exact module set. At minimum it records:

- `product_name`
- `edition_id`
- `display_version`
- `build_number`
- `update_build_revision`
- `build_lab_ex`
- `installation_type`
- `release_channel`

### Module Record

Each relevant loaded image has one module record.

| Field | Required | Meaning |
| --- | --- | --- |
| `module_id` | Yes | Stable ID unique within the build record |
| `role` | Yes | For example `shell`, `classic_taskbar`, `xaml_taskbar`, or `win32u` |
| `presence` | Yes | `required`, `allowed`, or `forbidden` for this profile |
| `module_name` | Yes | Lowercase base name |
| `path_expectation` | Yes | Canonical location relative to the Windows directory |
| `architecture` | Yes | PE machine, currently `amd64` only |
| `file_version` | Yes | Four-part version for evidence and exact comparison |
| `product_version` | Yes | Product version if present |
| `pe_timestamp` | Yes | PE COFF `TimeDateStamp`, encoded as hexadecimal |
| `size_of_image` | Yes | PE optional-header `SizeOfImage` |
| `sha256` | Yes | SHA-256 of the exact on-disk image captured from the VM |
| `codeview` | Yes | PDB name, GUID, and age from the PE debug directory |
| `signing` | Recommended | Authenticode signer and verification result for evidence |
| `targets` | Yes | Hook targets owned by this module; may be empty |

Expected path values are explicit, for example:

- `explorer.exe`: `%SystemRoot%\explorer.exe`
- `taskbar.dll`: `%SystemRoot%\System32\taskbar.dll`
- `Taskbar.View.dll`: the exact canonical path observed on the VM
- `ExplorerExtensions.dll`: the exact canonical path observed on the VM
- `win32u.dll`: `%SystemRoot%\System32\win32u.dll`

The generator must capture the path actually mapped into `explorer.exe`.
Maintainers must not guess package or component-store paths.

PDB identity is a strong exact-build discriminator, but no one field is
sufficient by itself. The runtime comparison uses all required identity
fields. File version remains useful, but a matching version alone never
selects a profile.

### Target Record

| Field | Required | Meaning |
| --- | --- | --- |
| `target_id` | Yes | Stable project-owned ID |
| `hook_profile_name` | Yes | Profile that owns the target |
| `kind` | Yes | `private-symbol` or `export` |
| `symbol_name` | Yes | Exact diagnostic symbol or export name |
| `decorated_name` | When available | Exact decorated PDB name |
| `resolved_rva` | Yes | Unsigned RVA from the mapped module base |
| `section_name` | Yes | Expected executable PE section |
| `entry_fingerprint` | Yes | Bytes and mask at a profile-defined offset |
| `prototype_id` | Yes | Project-owned ABI/prototype contract |
| `calling_convention_notes` | Yes | Review notes for the exact target |
| `resolution_evidence` | Yes | PDB identity and DIA result used to derive the RVA |

`entry_fingerprint` contains:

- `offset_from_rva`, normally `0`;
- `bytes`, encoded as lowercase hexadecimal;
- `mask`, where `ff` means compare and `00` means ignore;
- `length`;
- `rationale` for every masked byte.

Fingerprints are a second check, not a substitute for module identity.
Masking must be minimal and reviewed. A fingerprint that masks the entire
entry is invalid.

`calling_convention_notes` must state that x64 targets use the Microsoft x64
ABI even when source spellings use `__cdecl` or `WINAPI`. C++ instance methods
are represented by an explicit first `pThis` parameter in detour prototypes.
Return type, parameter count, width, ownership, and any WinRT value/reference
layout must be reviewed for the exact target. A matching name and RVA do not
prove ABI compatibility.

### Hook Profile

A hook profile is the indivisible behavior unit installed by the future
runtime.

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | Yes | Stable profile name |
| `behavior` | Yes | Must be `grouped-click-list` |
| `required_module_ids` | Yes | Modules that must be present and matched |
| `forbidden_module_ids` | Yes | Observations that invalidate the profile |
| `requirements` | Yes | Required targets and alternative sets |
| `late_module_policy` | Yes | Wait, timeout/status, unload, and reload behavior |
| `transaction_policy` | Yes | Must require one all-or-nothing commit |

A requirement is either:

- `all`: every listed target is required; or
- `exactly_one`: exactly one target from a known signature family is required.

The two known
`HoverFlyoutController::ShowTaskListButtonHoverFlyout` signatures are an
`exactly_one` family. The generator resolves which one exists in the exact
PDB. A runtime must never probe signatures or choose a prototype from a
Windows version number.

Initial profile names should describe behavior and ABI revision, not Windows
marketing releases, for example:

- `classic-list-on-click-x64-v1`
- `xaml-list-on-click-x64-v1`
- `xaml-list-on-click-pre-kb5053656-x64-v1`
- `mixed-list-on-click-x64-v1`

These names are schema examples, not evidence that any profile works on a
released build.

### Evidence Record

The `evidence` object keeps support promotion reviewable. It contains:

- `capture_id` and the external evidence-bundle location or archive digest;
- VM name and snapshot/checkpoint ID;
- capture operator and UTC time;
- generator commit and configuration digest;
- `capture_state`, such as `complete` or `failed`;
- reviewer identity, review time, and review report digest;
- `acceptance_state`, initially `not-run`;
- acceptance report and no-network trace digests when completed; and
- the repository commit containing the reviewed promotion.

A `validated` record without `capture_state == "complete"`,
`acceptance_state == "passed"`, and review/acceptance digests is structurally
invalid. The generator cannot create those approvals on its own.

### Illustrative Candidate Record

This abbreviated JSON is structural documentation only. Placeholder values are
deliberately non-runnable and the record remains `inventory-only`.

```json
{
  "schema_version": 1,
  "manifest_id": "candidate-example",
  "generated_at_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "generator": {
    "name": "symbol-manifest",
    "version": "not-implemented",
    "source_commit": "not-captured"
  },
  "source_revisions": {
    "taskbar_thumbnails_mod": "92d307593c5b7accafdb2bb3cf34df6f36d050c6",
    "windhawk": "b59b38cd77daec98830c0e5e2ad14a35c44f02a7",
    "minhook": "d94c64d32ea37bc4f5ee47d580709f70c6fb6080"
  },
  "build_records": [
    {
      "build_record_id": "unverified-placeholder",
      "support_state": "inventory-only",
      "support_note": "Example only; contains no captured local evidence.",
      "windows_release_label": "unverified",
      "os_identity": {
        "product_name": "Windows 11",
        "edition_id": "not-captured",
        "display_version": "not-captured",
        "build_number": "not-captured",
        "update_build_revision": "not-captured",
        "build_lab_ex": "not-captured",
        "installation_type": "Client",
        "release_channel": "not-captured"
      },
      "architecture": "amd64",
      "shell_scope": "explorer-only",
      "hook_profile_name": "unassigned",
      "modules": [],
      "hook_profiles": [],
      "evidence": {
        "capture_state": "not-captured",
        "acceptance_state": "not-run"
      }
    }
  ]
}
```

## Targets to Inventory

The inventory must resolve only targets needed by the one-purpose
`listOnClick` adaptation.

### Classic Taskbar Candidates

Module: `taskbar.dll`

- `CTaskListWnd::_DisplayExtendedUI`
- `CTaskListThumbnailWnd::_CanShowThumbnails`

The upstream tooltip hook is excluded.

### XAML Taskbar Candidates

Owning module: exactly identified as `Taskbar.View.dll` or
`ExplorerExtensions.dll` for the captured build.

- `HoverFlyoutModel::TransitionToFlyoutVisibleStickyState`
- exactly one known
  `HoverFlyoutController::ShowTaskListButtonHoverFlyout` signature
- `FlyoutFrame::CanFitAndUpdateScaleFactor`

### Export Candidates

Module: `win32u.dll`

- `NtUserShowWindow`
- `NtUserEnableWindow`

Although these are exports, the inventory records their resolved RVAs,
module identity, executable-section bounds, and fingerprints. A future runtime
may also call `GetProcAddress` and require its result to equal
`module base + resolved_rva`.

## Offline Generation Workflow

Generation is split so the test VM does not need network access.

1. Create or restore a disposable Windows 11 VM snapshot.
2. Disable its virtual network adapter before evidence capture.
3. Install all intended Windows updates before disconnecting the VM.
4. Verify no ExplorerPatcher, StartAllBack, Start11, Windhawk mod, or other
   shell customization is active.
5. Exercise the native grouped taskbar UI so late taskbar modules load.
6. Enumerate the exact modules mapped in the shell process and capture their
   canonical paths.
7. Copy the exact binaries to an evidence directory and record SHA-256 before
   analysis.
8. Supply matching PDBs through controlled offline media or a pre-populated
   local cache. Symbol acquisition, if needed, occurs on a separate maintainer
   machine and is not part of runtime or test-VM networking.
9. Verify each PDB GUID and age against the binary CodeView record before DIA
   loads it.
10. Use DIA with an explicit local PDB path. Do not configure `srv*`, symsrv,
    Windhawk caches, or a symbol server fallback.
11. Resolve the exact symbol names, convert addresses to RVAs, and require each
    RVA to fall within an executable section of its owning image.
12. Resolve required exports locally and record their RVAs.
13. Capture entry bytes, produce the smallest justified mask, and disassemble
    enough code to review instruction boundaries and obvious thunks.
14. Record prototype and calling-convention notes against the pinned upstream
    implementation.
15. Emit a deterministic candidate record and an evidence report.
16. Re-run generation from the same evidence directory and require byte-for-
    byte identical output.
17. Review the diff and complete
    `tests/manual/module-inventory-checklist.md`.
18. Keep the record `inventory-only` until the future implementation passes
    the full acceptance test on the same exact VM snapshot.

The generator should never modify or replace system files. It reads loaded
module metadata and copies evidence to a separate directory.

## Runtime Selection and Refusal Rules

The future runtime must perform the following checks before calling any
MinHook creation or enable function.

1. Parse the manifest with strict schema and bounds checks.
2. Require Windows 11, native `amd64`, and the verified current-user
   `explorer.exe` shell process.
3. Consider only records marked `validated`.
4. Enumerate the relevant loaded modules and canonicalize their final paths.
5. Compare every required module name, path, machine, file version, PE
   timestamp, `SizeOfImage`, SHA-256, and CodeView PDB name/GUID/age.
6. Enforce required, allowed, and forbidden module presence.
7. Require exactly one matching build record. Zero or multiple matches are
   unsupported.
8. Require the selected profile to be internally complete and to reference
   only modules and targets from that record.
9. For every target, reject arithmetic overflow, an RVA outside
   `SizeOfImage`, a non-executable section, or a fingerprint mismatch.
10. For an export target, require `GetProcAddress` to resolve and equal the
    validated `module base + RVA`; reject forwarded or unexpected results.
11. Require every `all` target and exactly one member of every `exactly_one`
    family.
12. Only after all checks pass, create every hook, queue every enable, and
    commit the complete profile once.

Any failure means:

- install and enable zero hooks;
- roll back every hook object created during the failed transaction;
- report `unsupported` for identity/profile/fingerprint failures or `error`
  for local operational failures;
- preserve native Explorer behavior;
- perform no symbol lookup, network request, or unbounded retry.

OS build, UBR, and Windows release label may be logged, but they must not relax
or replace module matching.

## Late-Loaded Module Handling

`Taskbar.View.dll` or `ExplorerExtensions.dll` may load after initialization.
The manifest handles this with an activation barrier:

- Initial module enumeration narrows the validated record set using identities
  that are already observable.
- If multiple validated records share the same observed prefix and differ only
  in a not-yet-loaded required module, retain that narrowed candidate set and
  wait. Ambiguity is allowed only while zero hooks exist.
- If a required late module is absent, status is `waiting-for-module` and zero
  hooks are installed.
- `LdrRegisterDllNotification`, when available, only places the relevant base
  name and module event into preallocated state.
- The loader callback performs no hashing, path canonicalization, symbol work,
  manifest parsing, logging through another module, IPC, allocation, or
  MinHook call.
- A worker thread rescans all relevant modules after notification.
- A rescan immediately after notification registration closes the initial
  scan/register race.
- Low-frequency worker polling is an allowed fallback when notification
  registration is unavailable.
- Once the complete exact module set is present, the worker repeats all
  identity, target, and fingerprint checks, requires exactly one complete
  record, and only then commits one transaction.

The runtime must not treat `Taskbar.View.dll` and `ExplorerExtensions.dll` as
interchangeable by name. The selected record says which module owns the XAML
targets and whether the other name is required, allowed, or forbidden.

If a required module unloads or reloads after activation, or a newly loaded
related module violates the selected record, the runtime must disable the
whole profile, drain active detours, remove all hooks, and return to
`waiting-for-module` or `unsupported`. It must not retain hooks into an
unloaded image or patch only the replacement module.

## Support Recording Policy

Windows release labels organize research; they do not grant support.

| Windows family | Current repository state | Rule |
| --- | --- | --- |
| Windows 11 23H2 | No captured local evidence; unsupported | Add exact build/UBR and module set only after VM capture |
| Windows 11 24H2 | No captured local evidence; unsupported | Treat every changed module identity as a new candidate |
| Newer Windows 11 releases | No captured local evidence; unsupported | Create a separate exact record; never inherit 24H2 status |
| Insider or preview builds | Unsupported | Require an explicit future policy and separate validation |

A validated record supports only its exact module set. It does not support:

- every installation with the same `23H2` or `24H2` label;
- a range of UBR values;
- a build whose file versions match but hashes or CodeView identities differ;
- a neighboring cumulative update;
- a system with an unreviewed shell customization;
- ARM64, Windows 10, or a non-Explorer shell.

When Windows Update changes any required identity, the runtime fails closed
until maintainers capture a new candidate and repeat validation. Retired
records remain useful for audit history but are excluded from release
manifests.

## Rollback and Uninstall Relationship

Manifest validation does not replace safe hook lifecycle handling. A future
implementation still must:

- create and enable a profile transactionally;
- disable the complete profile before removing any hook;
- wait for active detours to drain;
- unload only after MinHook removal succeeds;
- report `needs Explorer restart` when rollback cannot be confirmed; and
- stop uninstall before deleting loaded files when disable is unconfirmed.

An unsupported or mismatched build needs no rollback because it must never
enable a hook.

## Sources Reviewed

- Upstream `taskbar-thumbnails.wh.cpp`, revision
  `92d307593c5b7accafdb2bb3cf34df6f36d050c6`:
  <https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp>
- Windhawk symbol implementation, revision
  `b59b38cd77daec98830c0e5e2ad14a35c44f02a7`:
  <https://github.com/ramensoftware/windhawk/blob/b59b38cd77daec98830c0e5e2ad14a35c44f02a7/src/windhawk/engine/symbol_enum.cpp>
- Windhawk symbol API and hook documentation:
  <https://github.com/ramensoftware/windhawk/wiki/Creating-a-new-mod>
- Windhawk `HookSymbols` overview:
  <https://github.com/ramensoftware/windhawk/wiki/Development-tips>
- MinHook API, revision
  `d94c64d32ea37bc4f5ee47d580709f70c6fb6080`:
  <https://github.com/TsudaKageyu/minhook/blob/d94c64d32ea37bc4f5ee47d580709f70c6fb6080/include/MinHook.h>
