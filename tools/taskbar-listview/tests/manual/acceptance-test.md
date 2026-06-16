# Manual Acceptance Test

## Purpose

This test defines the minimum evidence required before claiming support for one
exact Windows 11 module set.

The repository currently has no implementation and no supported builds. These
steps are a gate for future work, not a claim that they pass today.

## Test Environment

Run in a disposable VM or recoverable test machine.

Record:

- Windows edition, version, OS build, and update revision.
- Architecture.
- `explorer.exe`, `taskbar.dll`, `Taskbar.View.dll`, and
  `ExplorerExtensions.dll` file versions.
- PE timestamp, image size, and PDB GUID/age for each relevant module.
- Manifest revision and selected hook profile.
- Tool commit and build configuration.
- Whether ExplorerPatcher, StartAllBack, Start11, or similar shell software is
  installed. Such systems are expected to be unsupported initially.

Use at least one grouped application with three distinguishable windows.

## Preconditions

- [ ] The exact module identities are present in the offline manifest.
- [ ] All required target fingerprints match before hooks are enabled.
- [ ] The test build is x64 Windows 11.
- [ ] No other taskbar customization or hook tool is active.
- [ ] A way to restart Explorer or sign out is available.
- [ ] Relevant logs are enabled.
- [ ] Network monitoring is available for the no-network check.

## Baseline

With the tool disabled:

- [ ] Hovering a grouped taskbar button shows native preview behavior.
- [ ] Clicking the grouped taskbar button shows native preview behavior.
- [ ] Clicking an ungrouped taskbar button activates/minimizes it normally.
- [ ] Task View, Start, Search, notification area, and taskbar context menus
      behave normally.
- [ ] Record screenshots or video of the baseline.

## Enable and Targeting

1. Start the launcher and enable the tool.
2. Capture launcher status and logs.

Pass criteria:

- [ ] Exactly one launcher instance runs in the current logon session.
- [ ] The target PID matches the process owning `GetShellWindow`.
- [ ] The verified target path is the Windows `explorer.exe`.
- [ ] No other process receives the DLL.
- [ ] The DLL reports the exact manifest profile and all required targets.
- [ ] Status becomes active only after the complete hook transaction commits.
- [ ] No elevation, service, driver, scheduled privileged task, or network
      access is used.

## Core Behavior

With three windows in one taskbar group:

- [ ] Hover does not display grouped-window thumbnails or a compact list.
- [ ] A normal left click displays the native compact text list.
- [ ] The list contains one selectable entry per open window.
- [ ] Selecting each entry activates the correct window.
- [ ] Repeated open/click/select cycles remain functional.
- [ ] Closing an entry updates the list correctly.
- [ ] Opening a new window updates the list correctly.
- [ ] No thumbnail images appear in the click list.

Repeat on every taskbar shown in a multi-monitor configuration:

- [ ] Main taskbar behaves correctly.
- [ ] Secondary taskbars behave correctly where Windows exposes grouped items.

## Regression Checks

- [ ] An ungrouped taskbar button still activates and minimizes normally.
- [ ] Middle-click behavior is unchanged.
- [ ] Shift-click behavior is unchanged.
- [ ] Right-click jump lists/context menus are unchanged.
- [ ] Keyboard taskbar navigation is unchanged.
- [ ] Task View hover/click is unchanged.
- [ ] Start and Search behavior is unchanged.
- [ ] Notification area flyouts are unchanged.
- [ ] Full-screen applications and auto-hide taskbar still work.
- [ ] Explorer remains responsive during rapid hover/click activity.

Any unrelated taskbar customization is a failure.

## Late Module Load

Use a test arrangement where the injected DLL initializes before
`Taskbar.View.dll` or `ExplorerExtensions.dll` is observed.

- [ ] Initial status is waiting/inactive, not partially active.
- [ ] Loader notification performs no hook or symbol work in the callback.
- [ ] Worker detects the late module.
- [ ] Exact identity and fingerprints are validated.
- [ ] The full declared profile commits once.
- [ ] Core behavior then passes.
- [ ] No duplicate hook is created after repeated reconciliation.

## Explorer Restart

While enabled:

1. Restart Explorer using a controlled test method.
2. Wait for the new shell window and PID.

Pass criteria:

- [ ] Old DLL and IPC state disappear with the old process.
- [ ] Launcher detects the exact process exit.
- [ ] Launcher finds and revalidates the new shell PID.
- [ ] DLL is injected only into the new shell.
- [ ] Core behavior passes after reinjection.
- [ ] No retry loop or duplicate launcher/DLL session appears.

## Disable Rollback

While the grouped click list is visible or immediately after rapid activity:

1. Disable the tool.
2. Observe status and native behavior.

Pass criteria:

- [ ] New late-module work is stopped.
- [ ] Hooks are disabled in one committed transaction.
- [ ] Active detour calls drain within the documented timeout.
- [ ] Hooks are removed and MinHook is uninitialized.
- [ ] DLL reports disabled and unloads.
- [ ] Native hover and click thumbnails return without restarting Explorer.
- [ ] Explorer remains responsive.
- [ ] Launcher does not report success before DLL acknowledgement.

## Host Crash Fail-Safe

1. Enable the tool and confirm active behavior.
2. Terminate only the launcher process to simulate a crash.

Pass criteria:

- [ ] DLL detects loss of the launcher handle.
- [ ] DLL performs orderly hook disable/removal.
- [ ] DLL unloads.
- [ ] Native behavior returns.
- [ ] Explorer remains running.

## Unsupported Build and Tamper Gating

Run each case separately:

- Remove the matching manifest entry.
- Change one expected target fingerprint in a test manifest.
- Remove one required target from a profile.
- Present a module identity from an untested Windows update.

Pass criteria for every case:

- [ ] Status is unsupported with a useful local diagnostic.
- [ ] Zero hooks are enabled.
- [ ] Native behavior is unchanged.
- [ ] No repeated symbol download or retry occurs.
- [ ] Explorer remains stable.

## No-Network Check

Monitor process network activity during:

- Launcher startup.
- First injection.
- Unsupported identity handling.
- Explorer restart and reinjection.
- Disable.

Pass criteria:

- [ ] Launcher opens no network connection.
- [ ] Injected DLL opens no network connection.
- [ ] No Microsoft symbol server, Windhawk cache, telemetry, update, DNS, or
      other runtime request occurs.

Local authenticated IPC does not count as network access, but remote named-pipe
access must be disabled.

## Uninstall

1. Enable and verify the tool.
2. Run the future uninstall/remove flow.

Pass criteria:

- [ ] Enabled state is cleared first.
- [ ] DLL confirms hooks removed and unloads.
- [ ] Per-user startup registration is removed.
- [ ] Launcher exits.
- [ ] Files and per-user state are removed as documented.
- [ ] Native behavior remains after a fresh Explorer restart and sign-in.
- [ ] If DLL shutdown cannot be confirmed, uninstall stops and clearly asks
      for an explicit Explorer restart or sign-out.

## Stress

For at least 30 minutes:

- Rapidly hover and click several grouped applications.
- Open and close windows while the list is visible.
- Move windows between monitors and virtual desktops.
- Toggle enable/disable at least 20 times.
- Restart Explorer at least 5 times.

Pass criteria:

- [ ] No Explorer crash, hang, leak trend, or corrupted taskbar state.
- [ ] No stale list entries or unselectable windows.
- [ ] No hook transaction or active-call drain timeout.
- [ ] Native behavior returns after the final disable.

## Evidence and Sign-Off

Attach:

- [ ] Environment and exact module identity report.
- [ ] Manifest/profile used.
- [ ] Launcher and DLL logs.
- [ ] Baseline and active behavior capture.
- [ ] Network trace summary.
- [ ] Explorer restart, disable, host-loss, and uninstall results.
- [ ] Known deviations.

A build may be added to the support list only when every required item passes.
Any changed module identity after Windows Update requires a new test run.
