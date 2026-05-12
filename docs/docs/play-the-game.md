# Play the Game

Use this page if you just want to install the release and play, without dealing with the build system.

## What you need

- A copy of the prebuilt ZIP from the latest GitHub release
- Your game folder, the one that already contains `default.xex` and `gen/`
- Optional: Xenia, if you want to play on PC

## Install on console or handheld setups

1. Download the prebuilt ZIP from the GitHub release.
2. Extract it into your game folder.
3. Launch `definitive.xex`.

If you want the base game hidden from the dashboard, back up `default.xex` first and then rename `definitive.xex` to `default.xex`.

## Install for Xenia on PC

1. Download the prebuilt ZIP from the GitHub release.
2. Copy `xenia/patches/373307D9 - Dance Central 3.patch.toml` from the ZIP into your Xenia installation's `patches/` folder.
3. Launch `definitive.xex` in Xenia.

If you renamed `definitive.xex` to `default.xex`, launch that file instead.

## What the ZIP contains

- `definitive.xex` for the rebuilt game
- `gen/` with the generated patch data
- `xenia/patches/373307D9 - Dance Central 3.patch.toml` for Xenia users

## If something goes wrong

If the game does not start, check [Troubleshooting](troubleshooting.md).