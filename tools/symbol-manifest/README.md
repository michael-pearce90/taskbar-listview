# Symbol Manifest Tool

## Status

Tooling contract only. No generator is implemented.

The future tool produces candidate offline symbol-manifest records. It does
not inject, hook, patch, download symbols, or declare Windows support.

## Responsibilities

The tool should:

- inspect exact copied Windows PE images;
- verify local PDB identity against each image's CodeView record;
- resolve an allowlisted set of private symbols through DIA;
- resolve allowlisted PE exports;
- convert addresses to RVAs;
- validate executable-section bounds;
- capture deterministic entry fingerprints;
- emit module identity and evidence reports;
- validate candidate and release manifests against the schema; and
- refuse all network-backed symbol paths.

The tool should not:

- accept arbitrary symbol names from an end-user runtime;
- search Microsoft or Windhawk symbol servers;
- infer compatibility from Windows version ranges;
- write to Windows system directories;
- load code into `explorer.exe`;
- install MinHook hooks; or
- change `support_state` to `validated` automatically.

## Proposed Commands

Command names are provisional.

```text
symbol-manifest capture --config targets.json --evidence <directory>
symbol-manifest resolve --evidence <directory>
symbol-manifest verify --candidate <manifest.json>
symbol-manifest diff --base <manifest.json> --candidate <manifest.json>
symbol-manifest compile --release <validated-manifest.json> --out <file>
```

`capture` may run on the isolated test VM to collect OS data, loaded-module
paths, copied binaries, hashes, and PE identity.

`resolve` operates only on the evidence directory and explicit local PDB
paths. It must work with the test VM network adapter disabled.

`verify` performs schema, identity, RVA, section, fingerprint, profile, and
provenance consistency checks without changing the input.

`compile` must reject every build record whose `support_state` is not
`validated`.

## Inputs

### Target Allowlist

The source-controlled target configuration contains stable target IDs and
exact symbol-name alternatives derived from the pinned upstream mod. It should
include only:

- `CTaskListWnd::_DisplayExtendedUI`
- `CTaskListThumbnailWnd::_CanShowThumbnails`
- `HoverFlyoutModel::TransitionToFlyoutVisibleStickyState`
- the two known `ShowTaskListButtonHoverFlyout` signatures
- `FlyoutFrame::CanFitAndUpdateScaleFactor`
- `NtUserShowWindow`
- `NtUserEnableWindow`

No tooltip, virtual desktop, ExplorerPatcher, old-taskbar, or broad taskbar
feature targets belong in the allowlist.

### Evidence Directory

The evidence directory contains copied module images, matching PDBs, VM
capture metadata, and review notes. It is local input, not a symbol cache that
the runtime can query.

At minimum the tool requires:

- exact module path observed in `explorer.exe`;
- exact copied image;
- SHA-256;
- PE machine, timestamp, and `SizeOfImage`;
- file and product version;
- CodeView PDB name, GUID, and age;
- matching local PDB for private-symbol modules;
- OS build/UBR metadata; and
- capture provenance.

## Local-Only Symbol Resolution

The resolver should use DIA with an explicit PDB file selected after CodeView
GUID/age verification. It must not call `loadDataForExe` with an `srv*` search
path or allow a fallback to symsrv.

Recommended enforcement:

- accept only absolute local image and PDB paths;
- reject URL and `srv*` syntax;
- do not ship or load `symsrv.dll`;
- disable DIA symbol-server access through its load callback where applicable;
- log the exact PDB path and identity used;
- fail when the local PDB is absent or mismatched; and
- include a test that generation succeeds with all network adapters disabled.

PDB acquisition may occur separately on a maintainer workstation. It is a
controlled preparation step, not part of this tool's VM capture mode and never
part of the end-user runtime.

## Address Rules

For every resolved target:

1. Obtain the symbol virtual address or export address from the exact image.
2. Subtract the image base to obtain an unsigned RVA.
3. Reject underflow, overflow, and RVAs at or beyond `SizeOfImage`.
4. Find the containing PE section.
5. Require an executable section and a range large enough for the fingerprint.
6. Reject duplicate target addresses unless a reviewed alias is explicitly
   represented by the schema.
7. Store the RVA, never a process-specific virtual address.

A future runtime calculates the hook address only as:

```text
validated loaded module base + validated RVA
```

For exports, the runtime additionally requires `GetProcAddress` to return that
same address.

## Fingerprint Rules

The generator should default to a short sequence of complete x64 instructions
at or near the entry point. It must not split an instruction.

Masks are allowed only for bytes whose variability is understood, such as a
reviewed relative displacement. Each masked range needs a rationale.

Reject:

- all-zero masks;
- fingerprints outside executable sections;
- fingerprints shorter than the configured minimum;
- masks generated merely to make two different builds compare equal; and
- fingerprints copied from a neighboring build without regenerating them.

The candidate report should include disassembly beside the bytes so a reviewer
can detect an import thunk, jump stub, hotpatch pattern, or implausible
prototype.

## Profile Assignment

The tool may propose a profile from resolved target sets, but a maintainer must
approve it.

- A classic profile requires both classic private targets.
- An XAML profile requires the sticky transition, fit check, exactly one hover
  signature, and both `win32u.dll` exports.
- A mixed profile requires every target declared by that exact tested path.
- Missing required targets produce a failed candidate, not a reduced profile.
- Both hover signatures resolving unexpectedly requires manual investigation.

`Taskbar.View.dll` and `ExplorerExtensions.dll` are separate identities. The
capture records which is loaded, which owns symbols, and whether the other is
required, allowed, or forbidden.

## Deterministic Output

For identical input evidence and tool version:

- object keys use a fixed order;
- arrays use schema-defined ordering;
- hexadecimal uses lowercase with a consistent `0x` policy;
- GUIDs use a single canonical format;
- paths use a documented Windows canonical form;
- timestamps are UTC;
- no absolute maintainer-machine paths appear in committed output; and
- two runs produce byte-for-byte identical candidate JSON.

Generation time may be supplied through a reproducible build environment or
stored in a detached evidence report if it would otherwise break
determinism.

## Validation Failures

The tool exits nonzero and emits no runtime-eligible output when:

- the schema version is unknown;
- a module or target ID is duplicated;
- an image is not native `amd64`;
- an expected module name/path does not match capture metadata;
- a PDB GUID/age does not match;
- a symbol or export is absent or ambiguous;
- an RVA is outside its image or executable section;
- a fingerprint is missing or invalid;
- profile requirements are incomplete;
- evidence provenance is missing;
- a candidate claims `validated` without recorded acceptance sign-off; or
- any network-backed symbol configuration is detected.

Partial output may be written only as a clearly marked failed research report,
never as a release manifest.

## Security and Licensing

Treat evidence directories as untrusted parser input even when maintainers
created them. Use bounded PE/PDB parsing and reject unreasonable counts,
offsets, sizes, and path lengths.

The project is GPLv3. Any implementation adapted from the upstream
`taskbar-thumbnails.wh.cpp` behavior must retain the required attribution.
Windhawk runtime code is not needed for this generator. If MinHook is later
used by the runtime, retain its BSD-2-Clause notice; MinHook is not needed for
offline resolution.

Do not commit Microsoft binaries or PDBs unless redistribution rights are
confirmed. Commit hashes and generated metadata instead.

## Related Documents

- [Offline symbol manifest design](../../docs/design/offline-symbol-manifest.md)
- [Windows module inventory](../../docs/research/windows-module-inventory.md)
- [Module inventory checklist](../../tests/manual/module-inventory-checklist.md)
- [Manual acceptance test](../../tests/manual/acceptance-test.md)
