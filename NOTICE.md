# Notices

## Project License

Taskbar Click List is licensed under the GNU General Public License version 3
only (`GPL-3.0-only`). See `LICENSE`.

## Windhawk Mod Attribution

The research and proposed behavior are based on inspection of:

- **Disable Taskbar Thumbnails**, version 1.2
- File: `mods/taskbar-thumbnails.wh.cpp`
- Author: Michael Maltsev (`m417z`)
- Upstream repository: <https://github.com/ramensoftware/windhawk-mods>
- Reviewed revision:
  `92d307593c5b7accafdb2bb3cf34df6f36d050c6`
- Source:
  <https://github.com/ramensoftware/windhawk-mods/blob/92d307593c5b7accafdb2bb3cf34df6f36d050c6/mods/taskbar-thumbnails.wh.cpp>
- Upstream notice: "Source code is published under The GNU General Public
  License v3.0."

As of June 14, 2026, this repository contains documentation only and does not
copy Windhawk runtime source or the mod's hook implementation.

If implementation code is later adapted from the mod, source files must:

1. Retain the upstream copyright and authorship information.
2. State that the files were modified and give the relevant modification date.
3. Remain licensed under GPL version 3.
4. Link to the exact upstream revision used as the adaptation base.

This project is independent and is not endorsed by or affiliated with
Windhawk, Ramen Software, or Michael Maltsev.

## Windhawk Runtime

Windhawk was inspected to understand the API surface used by the mod. The
proposed standalone design does not require copying Windhawk's injection,
symbol, settings, lifecycle, or hook-management runtime code.

## Possible MinHook Dependency

MinHook has not been vendored in this documentation spike. If added later, its
BSD-2-Clause license and copyright notices must be distributed with source and
binaries.

- Project: <https://github.com/TsudaKageyu/minhook>
- Reviewed revision:
  `d94c64d32ea37bc4f5ee47d580709f70c6fb6080`
- License:
  <https://github.com/TsudaKageyu/minhook/blob/d94c64d32ea37bc4f5ee47d580709f70c6fb6080/LICENSE.txt>

Windows and related names are trademarks of Microsoft. Their use describes the
platform targeted by this project.
