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
- `--xenia-path <path>` path to Xenia executable
- `--xenia-run 0..4` auto-launch selected build in Xenia
- `--xenia-patch` create/update Xenia patch file
- `--xenia-args "..."` pass extra args to Xenia

## Wrapper scripts

- `scripts/build.sh`: Linux/macOS wrapper for default build
- `scripts/build.bat`: Windows wrapper for default build

Both wrappers call `tools/build.py` with `src bin`.
