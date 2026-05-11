# Xenia Integration

## What is supported

The build tool can:

- generate/update a DC3 patch TOML in Xenia `patches/`
- launch a selected XEX after build

## Required flags

- `--xenia-path <path>` must point to your Xenia executable/AppImage
- `--xenia-run` chooses what to run

Run selector values:

- `0` = disabled
- `1` = `deluxe.xex`
- `2` = `vanilla.xex`
- `3` = `deluxe_debug.xex`
- `4` = `vanilla_debug.xex`

## Example

```bash
./tools/build.py src bin \
  --vanilla --debug \
  --xenia-path ./xenia/xenia.AppImage \
  --xenia-patch \
  --xenia-run 1 \
  --xenia-args "--fullscreen"
```

## Patch behavior

When `--xenia-patch` is enabled, the build attempts to maintain patch content and append known module hashes for generated XEX variants.

Patch target location is based on the Xenia executable parent directory:

- `<xenia_root>/patches/373307D9 - Dance Central 3.patch.toml`

## Common pitfalls

- `--xenia-run` without `--xenia-path` is invalid.
- Launch fails if selected XEX was not built/copied to `out/`.
- Use absolute paths when testing from different working directories.
