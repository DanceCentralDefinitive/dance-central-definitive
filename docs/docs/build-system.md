# Build System

## Core pipeline

The build pipeline is orchestrated by `tools/build.py` and powered by Ninja.

High-level flow:

1. Clean/create working directories.
2. Copy filtered source data from `src/` to `obj/src/`.
3. Generate build rules into `build.ninja`.
4. Convert/copy files into `obj/ark/` and `obj/raw/`.
5. Pack output ark/hdr into `out/gen/`.
6. Copy selected XEX binaries into `out/`.
7. Optionally generate Xenia patch and run Xenia.

## File conversion behavior

- `.png` -> converted with `superfreq` to `.png_xbox`
- `.dta` -> validated with `dtacheck`, serialized and encrypted via `dtab` to `.dtb`
- Other files -> copied as-is

Platform-specific tools are selected from:

- `tools/linux/`
- `tools/macos/`
- `tools/windows/`

## Build variants

By default, the build includes `deluxe` retail.

Flags add more variants:

- `--vanilla` adds vanilla retail
- `--debug` adds debug builds for whichever families are enabled

## CLI reference

```bash
./tools/build.py src bin [options]
```

Common options:

- `--output <dir>` set output root
- `--includes <dir>` include additional files in output
- `--clean` remove generated cache directories after successful build
- `--allow-dtacheck-errors` keep building even if `dtacheck` reports errors
- `--patch-output <dir>` copy Xenia patch to directory
- `--xenia-root <path>` Xenia root directory (patch will be copied to patches/ subdirectory)
- `--xenia-path <path>` path to Xenia executable
- `--xenia-run 0..4` auto-launch selected build in Xenia
- `--xenia-args "..."` pass extra args to Xenia

## Wrapper scripts

- `scripts/build.sh`: Linux/macOS wrapper for default build
- `scripts/build.bat`: Windows wrapper for default build

Both wrappers call `tools/build.py` with `src bin`.

## Installation

### Prebuilt release ZIP

1. Download the prebuilt ZIP from the GitHub release.
2. Extract it into your game folder, the one that already contains `default.xex` and `gen/`.
3. Launch `definitive.xex`.

Optional: Back up `default.xex` and rename `definitive.xex` to `default.xex` if you want the base game hidden from the dashboard.

The ZIP also includes the Xenia patch under `xenia/patches/373307D9 - Dance Central 3.patch.toml`.

### With Xenia emulator

1. Download the prebuilt ZIP from the GitHub release.
2. Copy `xenia/patches/373307D9 - Dance Central 3.patch.toml` from the ZIP into your Xenia installation's `patches/` folder.
3. Launch `definitive.xex` (or `default.xex` if renamed) through Xenia.
