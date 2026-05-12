# Dance Central Definitive Documentation

This documentation covers the full build and content workflow for this repository.

If you only want to install and play the game, start with [Play the Game](play-the-game.md).

Use it as the source of truth for:

- preparing your environment,
- building patch output,
- managing source data changes,
- testing in Xenia,
- troubleshooting common issues.

## Scope

The project is centered around converting and packaging game data from `src/` into a deployable output tree in `out/`.

The build system supports:

- multiple XEX variants (deluxe/vanilla, retail/debug),
- platform-specific tool binaries (Linux/macOS/Windows),
- optional include overlays,
- optional Xenia patch generation and launch.

## Read this first

Start with [Getting Started](getting-started.md), then continue to [Build System](build-system.md).

If you are changing gameplay data or assets, review [Modding Workflow](modding-workflow.md).

If something fails, check [Troubleshooting](troubleshooting.md).

For licensing and IP scope, read [Legal and Licensing](legal.md).
