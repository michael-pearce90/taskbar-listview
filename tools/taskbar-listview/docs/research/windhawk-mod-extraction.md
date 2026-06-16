# Windhawk Mod Extraction Research

## Executive Summary

Adapting the one-purpose `listOnClick` behavior is technically feasible without
forking Windhawk or copying its runtime code.

The behavior-specific detours are small. Windhawk's substantial contribution
is the surrounding platform: process targeting and injection, mod lifecycle,
batched hook management, private-symbol download and caching, settings, and
automatic cleanup. A standalone project must replace those capabilities, but
it can do so narrowly for one x64 DLL in the current user's shell.

The recommended boundary is:

- Adapt only the GPLv3 hook behavior needed for grouped-click list mode.
- Use a small, independently maintained detour library such as MinHook.
- Implement a purpose-built launcher and injected DLL from scratch.
- Replace Windhawk symbol services with an offline, exact-module manifest.
- Support no build until its complete hook profile passes manual testing.

## Research Snapshot

Research was performed on June 14, 2026.

Primary source revisions inspected:

| Source | Revision |
| --- | --- |
| `ramensoftware/windhawk-mods` | repository tip `c780b0a668666da572a14c43a7e8f8f22f84cb5d`; mod's latest commit `92d307593c5b7accafdb2bb3cf34df6f36d050c6` |
| `ramensoftware/windhawk` | `b59b38cd77daec98830c0e5e2ad14a35c44f02a7` |
| `TsudaKageyu/minhook` | `d94c64d32ea37bc4f5ee47d580709f70c6fb6080` |

The mod was at version 1.2. That release added the exact desired
`listOnClick` mode and noted compatibility work for newer Windows 11 builds.

## Desired Behavior in the Upstream Mod

The standalone tool needs only the upstream mode named `listOnClick`:

- A non-persistent hover request is suppressed.
- A persistent click request is allowed.
- The native flyout is told that thumbnails cannot be shown or fitted, causing
  the native compact list representation.

There are two taskbar implementations to account for.

### Classic Taskbar Path

For the classic taskbar flyout, the mod:

1. Hooks `CTaskListWnd::_DisplayExtendedUI`.
2. Returns success without displaying UI for non-persistent requests.
3. Allows persistent requests to continue.
4. Hooks `CTaskListThumbnailWnd::_CanShowThumbnails`.
5. Returns false so the persistent flyout uses a list.

`CTaskListWnd::_ShowToolTip` supports a separate tooltip setting and is not
needed by this project.

### New XAML Flyout Path

For newer Windows 11 taskbar flyouts, the mod:

1. Hooks `HoverFlyoutController::ShowTaskListButtonHoverFlyout` to identify the
   hover call and its thread.
2. Hooks `NtUserShowWindow` and `NtUserEnableWindow` while that hover call is
   active, delaying visibility and enablement.
3. Hooks
   `HoverFlyoutModel::TransitionToFlyoutVisibleStickyState` so a click can
   transition the delayed window to the sticky state and then apply the
   pending show/enable operations.
4. Hooks `FlyoutFrame::CanFitAndUpdateScaleFactor` and returns false, selecting
   the compact list rather than thumbnails.

The source contains two signatures for
`ShowTaskListButtonHoverFlyout`: the current form and a pre-KB5053656 form
identified by the source as predating March 27, 2025. Only the signature that
exists in the exact target module should be installed.

## Windhawk-Specific Dependencies

The following list covers every Windhawk-specific facility directly or
implicitly used by `taskbar-thumbnails.wh.cpp`.

| Dependency | How the mod uses it | Replacement |
| --- | --- | --- |
| Windhawk metadata `@include explorer.exe` | Selects the target process | Launcher identifies only the current shell PID |
| `@architecture x86-64` | Restricts loading to x64 | Launcher and DLL reject non-x64 targets |
| `@compilerOptions -lversion` | Links version APIs | Normal MSVC/CMake linker configuration |
| `#include <windhawk_utils.h>` | Supplies typed hook and symbol helpers | Project-owned narrow wrappers |
| `Wh_ModInit` | Loads settings, checks build, registers initial hooks | DLL worker `Initialize` state transition |
| `Wh_ModAfterInit` | Handles races after initial hooks are applied | Post-commit module rescan on the DLL worker |
| `Wh_ModUninit` | Lifecycle endpoint after Windhawk removes hooks | Explicit shutdown followed by DLL unload |
| `Wh_ModSettingsChanged` | Reloads settings or requests a mod reload | Not needed; this tool has one fixed behavior |
| `Wh_Log` | Diagnostic logging | ETW, `OutputDebugStringW`, or a small local log |
| `Wh_GetStringSetting` | Reads `mode` | Not needed; behavior is always `listOnClick` |
| `Wh_FreeStringSetting` | Releases Windhawk's setting string | Not needed |
| `Wh_GetIntSetting` | Reads unrelated optional settings | Not needed |
| `WindhawkUtils::SYMBOL_HOOK` | Declares symbol names, originals, detours, and optionality | Project-owned static hook profile records |
| `HookSymbols` / `WindhawkUtils::HookSymbols` | Resolves private symbols, caches offsets, and registers hooks | Offline exact-module manifest plus detour wrapper |
| `WindhawkUtils::Wh_SetFunctionHookT` | Typed wrapper around hook registration | Small templated wrapper over MinHook |
| `Wh_SetFunctionHook` | Registers ExplorerPatcher export hooks | Drop ExplorerPatcher support |
| `Wh_ApplyHookOperations` | Commits hooks added after initialization | MinHook queue plus `MH_ApplyQueued` |
| Implicit hook commit after `Wh_ModInit` | Applies the initial queued hooks | Explicit transaction in DLL initialization |
| Automatic hook removal before `Wh_ModUninit` | Restores original code on unload | Explicit disable, quiesce, remove, uninitialize |
| Windhawk injection engine | Loads the compiled mod into matching processes | Narrow current-shell injector |
| Windhawk process/restart management | Loads mods into existing and future target processes | Persistent per-user launcher watches shell PID |
| Windhawk symbol service | Local cache, online cache, Microsoft PDB retrieval, enumeration | Offline manifest; no runtime network |
| Windhawk settings/storage | Persists and distributes mod settings | Minimal per-user enabled state only |
| Windhawk compiler/mod packaging | Compiles a `.wh.cpp` into a mod DLL | Normal standalone build system |

## Dependencies by Difficulty

### 1. Easy to Stub or Remove

- `Wh_Log`: replace with a tiny logger.
- Settings calls: remove them because there is one fixed mode.
- Mod callbacks: map to explicit `Initialize`, `Start`, and `Shutdown`
  functions on a DLL worker thread.
- Metadata and compiler options: express in the build and launcher.
- `Wh_ModAfterInit`: replace with a post-hook rescan.
- Version resource reading: it already uses ordinary Win32 APIs.

These items do not justify copying Windhawk runtime code.

### 2. Replaceable With a Small Library

- `Wh_SetFunctionHook`, the typed wrapper, queued enable/disable, trampolines,
  and hook removal can be provided by upstream MinHook.
- A project-owned wrapper can enforce typed target/original/detour records and
  all-or-nothing hook transactions.

MinHook is x86/x64 only, which is acceptable for the proposed x64-only scope.
Its BSD-2-Clause license is compatible with distribution in a GPLv3 project
when the MinHook notices are retained.

### 3. Hard Because Windhawk Provides Substantial Plumbing

- Reliably finding and injecting into the correct `explorer.exe`.
- Reinjecting after Explorer restarts.
- Resolving private C++ symbols across Windows builds.
- Downloading and caching PDB data. This project deliberately will not
  reproduce that networked behavior.
- Handling modules that load after the DLL initializes.
- Applying late hooks without racing the loader.
- Safely disabling hooks while detours may be executing.
- Unloading the DLL without leaving patched code or live callbacks.
- Coordinating settings, host lifetime, and cleanup across processes.

These are the core risks of the standalone project. They need original,
purpose-built code and build-specific tests, not pieces copied out of the
general Windhawk engine.

## Hook Targets Found

### Private Symbol Hooks

| Module | Target | Upstream purpose | Needed here |
| --- | --- | --- | --- |
| `Taskbar.View.dll` or `ExplorerExtensions.dll` | `HoverFlyoutModel::TransitionToFlyoutVisibleStickyState(winrt::hstring)` | Releases delayed XAML flyout when it becomes sticky | Yes, XAML profile |
| Same | `HoverFlyoutController::ShowTaskListButtonHoverFlyout(..., InputDeviceKind, TaskbarFlyoutKind)` | Marks the current XAML hover call | Yes, XAML profile |
| Same | Pre-KB5053656 `ShowTaskListButtonHoverFlyout(..., InputDeviceKind)` | Older signature of the same operation | Build-specific alternative |
| Same | `FlyoutFrame::CanFitAndUpdateScaleFactor(IVector<IInspectable> const&)` | Forces list fallback | Yes, XAML profile |
| `taskbar.dll` on Windows 11 | `CTaskListWnd::_DisplayExtendedUI(ITaskBtnGroup*, int, unsigned long, int)` | Suppresses non-persistent hover | Yes, classic profile |
| `taskbar.dll` on Windows 11 | `CTaskListThumbnailWnd::_CanShowThumbnails(CDPA<...> const*, int, int)` | Forces list fallback | Yes, classic profile |
| `taskbar.dll` on Windows 11 | `CTaskListWnd::_ShowToolTip(ShowToolTipFlags)` | Optional tooltip suppression | No |

The upstream source marks the `taskbar.dll` symbols optional and says
`_DisplayExtendedUI` and `_ShowToolTip` were removed in
`10.0.26100.8313`. This is direct evidence that file-version ranges are too
coarse and that hook profiles must be tied to exact module identities.

### Export/API Hooks

| Module | Export | Upstream purpose | Standalone decision |
| --- | --- | --- | --- |
| `win32u.dll` | `NtUserShowWindow` | Delays XAML hover flyout visibility | Retain for XAML profile |
| `win32u.dll` | `NtUserEnableWindow` | Delays XAML hover flyout enablement | Retain for XAML profile |
| `kernelbase.dll` | `LoadLibraryExW` | Detects late taskbar and ExplorerPatcher modules | Replace with module notification/rescan |

`user32.dll!GetWindowBand` is dynamically resolved but is only used for the
unrelated virtual desktop switcher option. It is not required here.

### ExplorerPatcher Export Hooks

The mod also looks for decorated exports corresponding to:

- `CTaskListWnd::_DisplayExtendedUI`
- `CTaskListThumbnailWnd::_CanShowThumbnails`
- `CTaskListWnd::_ShowToolTip`

ExplorerPatcher and old-taskbar support are out of scope. All related module
enumeration, `ep_taskbar.*` detection, and export hooking should be removed.

## Minimum Standalone Pieces

### Launcher

A per-user x64 process owns enable/disable state, locates the current shell,
injects the DLL, monitors the shell process handle, and coordinates shutdown.
It does not need elevation, a service, a driver, or broad process enumeration.

### Explorer Targeting

Use `GetShellWindow` and `GetWindowThreadProcessId` to identify the shell
instance. Then verify:

- Image path resolves to the Windows `explorer.exe`.
- Process session matches the launcher's interactive session.
- Target user SID matches the launcher.
- Target machine is x64.

Do not inject into every process named `explorer.exe`.

### Injected DLL

The DLL contains only behavior state, module detection, manifest validation,
hook functions, a MinHook wrapper, local IPC, and orderly shutdown. Heavy work
must run outside `DllMain`.

### Hook Wrapper

The wrapper needs:

- Typed hook records.
- Create/queue/commit as one transaction.
- Rollback when any required hook fails.
- Queue-disable, quiesce, remove, and uninitialize.
- Per-detour active-call counters to make unload observable and bounded.

### Symbol Lookup

Runtime symbol download is out of scope. Use an offline manifest generated
during development from symbols, keyed by exact PE/CodeView identity. Each
entry contains the function RVA and expected entry bytes or a masked
fingerprint.

An unknown identity, missing required target, or fingerprint mismatch is
unsupported and must install zero hooks.

DbgHelp or DIA may be used by a separate maintainer tool to produce manifest
entries. They are not required in the end-user runtime.

### Late `Taskbar.View.dll` / `ExplorerExtensions.dll` Handling

Perform an initial module scan, register for DLL load notification, and rescan
after initial hooks commit. The loader callback must not resolve symbols,
allocate complex state, log through other modules, or install hooks. It should
only record a preallocated notification for a worker thread.

Because `LdrRegisterDllNotification` is documented as subject to change, a
simple worker-side polling fallback is appropriate. The entire Explorer
process restart remains the main recovery boundary.

### Explorer Restart Handling

The launcher waits on the exact shell process handle. On exit:

1. Discard the old IPC/session state.
2. Wait for a new shell window and PID.
3. Re-run all identity and architecture checks.
4. Inject only if the tool remains enabled.

Each Explorer process is a fresh compatibility decision.

### Disable and Uninstall Rollback

Disable must instruct the DLL to:

1. Stop accepting late-module work.
2. Unregister DLL notifications.
3. Queue-disable and commit all hooks.
4. Wait for active detours to drain.
5. Remove hooks and uninitialize MinHook.
6. Close IPC and unload itself from a dedicated worker thread.

Uninstall first disables the tool and waits for acknowledgement. If the
injected DLL cannot acknowledge, uninstall must stop and offer an explicit
Explorer restart or sign-out rather than claiming rollback succeeded.

## Can Windhawk Runtime Code Be Avoided?

**Yes.**

No Windhawk runtime source is necessary for the proposed architecture:

- Injection can use documented process/memory/thread APIs in a narrow launcher.
- MinHook supplies the detour mechanics.
- A local manifest replaces Windhawk's symbol service.
- Fixed behavior eliminates Windhawk settings and mod packaging.
- A small state machine replaces the generic mod lifecycle.

The GPLv3 behavior code can be adapted with attribution while the standalone
host is independently implemented. Avoiding Windhawk runtime code also avoids
pulling in general process targeting, online symbol caches, mod compilation,
and unrelated engine complexity.

This conclusion does not mean the host is trivial. Injection, exact symbol
identity, and safe unload remain high-risk engineering areas.

## Licensing and Attribution

- The upstream mod explicitly states GPLv3. Adapting its hook implementation
  makes the resulting project a GPLv3 work.
- Use `GPL-3.0-only` conservatively because the mod says version 3.0 without
  granting an "or later" option.
- Preserve upstream author/source notices and mark modified files with dates.
- Distribute complete corresponding source and build scripts with binaries.
- Do not imply endorsement by Windhawk or the original author.
- If MinHook is vendored or distributed, retain its BSD-2-Clause notices.
- Do not copy Windhawk engine code unless a later design decision proves it
  necessary; this spike found no such necessity.

This is an engineering summary, not legal advice.

## Feasibility Verdict

**Conditional go for a prototype.**

Proceed only with these conditions:

- No supported-build claim until a complete hook profile is manually tested.
- Exact module identity and function fingerprints gate every installation.
- No runtime symbol downloads or other network access.
- No partial hook profile is allowed.
- Disable and host-loss rollback are implemented before normal distribution.
- ExplorerPatcher, old taskbar, Windows 10, ARM64, and Insider builds remain
  unsupported unless separately researched and tested.

## Recommended Next Task

Build an **offline symbol-manifest generator and compatibility inventory**, not
the injector.

For a small set of candidate Windows 11 test VMs:

1. Record OS build and the exact identities of `taskbar.dll`,
   `Taskbar.View.dll`, and `ExplorerExtensions.dll`.
2. Resolve only the six required private targets.
3. Record RVAs, PDB GUID/age, PE timestamp, image size, and target-entry
   fingerprints.
4. Determine which coherent hook profile applies to each build.
5. Commit the manifest schema and generated sample data with no runtime code.

That task tests the largest feasibility assumption before injection work
begins.

## Unresolved Issues

- Which released Windows 11 builds still use the classic path, the XAML path,
  or both?
- Does every desired build publish usable symbols for all required private
  targets?
- Are the inferred calling conventions and parameter layouts stable on each
  exact module identity?
- Can all target systems cleanly unload MinHook detours from Explorer under
  realistic taskbar activity?
- Will security products block or quarantine the narrow injector?
- Does returning false from `CanFitAndUpdateScaleFactor` always select a list,
  or can future builds choose a different fallback?
- Is DLL load notification sufficiently reliable for taskbar component reload,
  or should the worker use periodic module reconciliation?
- What user experience should be used when disable requires an Explorer
  restart?

## Sources

- Upstream mod source:
  <https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp>
- Upstream v1.2 change:
  <https://github.com/ramensoftware/windhawk-mods/commit/92d307593c5b7accafdb2bb3cf34df6f36d050c6>
- Windhawk mod creation/API documentation:
  <https://github.com/ramensoftware/windhawk/wiki/Creating-a-new-mod>
- Windhawk mod lifecycle:
  <https://github.com/ramensoftware/windhawk/wiki/Mod-lifetime>
- Windhawk development tips and `HookSymbols` description:
  <https://github.com/ramensoftware/windhawk/wiki/Development-tips>
- Windhawk mod API at reviewed revision:
  <https://github.com/ramensoftware/windhawk/blob/b59b38cd77daec98830c0e5e2ad14a35c44f02a7/src/windhawk/engine/mods_api.h>
- Windhawk symbol implementation at reviewed revision:
  <https://github.com/ramensoftware/windhawk/blob/b59b38cd77daec98830c0e5e2ad14a35c44f02a7/src/windhawk/engine/mod.cpp>
- Windhawk symbol enumeration at reviewed revision:
  <https://github.com/ramensoftware/windhawk/blob/b59b38cd77daec98830c0e5e2ad14a35c44f02a7/src/windhawk/engine/symbol_enum.cpp>
- MinHook:
  <https://github.com/TsudaKageyu/minhook/tree/d94c64d32ea37bc4f5ee47d580709f70c6fb6080>
- Microsoft `LdrRegisterDllNotification` documentation:
  <https://learn.microsoft.com/windows/win32/devnotes/ldrregisterdllnotification>
- Microsoft `LdrDllNotification` callback warning:
  <https://learn.microsoft.com/windows/win32/devnotes/ldrdllnotification>
- Microsoft symbol lookup overview:
  <https://learn.microsoft.com/windows/win32/debug/finding-symbols>
- GNU GPLv3 text:
  <https://www.gnu.org/licenses/gpl-3.0.txt>
