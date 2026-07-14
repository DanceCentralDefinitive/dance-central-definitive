# Dance Central Definitive

[![Discord Server](https://dcbadge.limes.pink/api/server/https://discord.gg/Bj94CECgcK)](https://discord.gg/Bj94CECgcK)

Dance Central Definitive is a patch/mod workspace for Dance Central 3 content, packaging, and testing.
The repository contains source game data (`src/`), build tooling (`tools/build.py`), helper scripts (`scripts/`), and docs (`docs/`).

**📖 [Read the full docs](https://dancecentraldefinitive.github.io/dance-central-definitive/)**

## What this project does

- Builds Xbox 360 patch arks from `src/` content.
- Converts supported source formats (for example `.dta` to encrypted `.dtb`, `.png` to `.png_xbox`).
- Selects and packages matching XEX binaries from `bin/`.
- Optionally generates/updates a Xenia patch file and launches a selected build in Xenia.

## Quick start

### Linux / macOS

```bash
./scripts/build.sh
```

### Windows

```bat
scripts\build.bat
```

Default build output is written to `out/`.

## Build options

Use the Python tool directly for all options:

```bash
./tools/build.py src bin --help
```

Common options:

- `--debug`: include debug variants.
- `--vanilla`: include vanilla variants in addition to definitive.
- `--includes <dir>`: copy extra files into the output tree.
- `--output <dir>`: change output directory (default: `out`).
- `--clean`: remove generated caches after a successful build.
- `--xenia-path <path>`: path to Xenia executable.
- `--xenia-run {0..4}`: select which XEX to run (0 disables run).
- `--xenia-patch`: create/update Xenia patch TOML.
- `--xenia-args "..."`: extra command-line args for Xenia.

Example:

```bash
./tools/build.py src bin --vanilla --debug --xenia-path ./xenia/xenia.AppImage --xenia-run 1
```

## Helper scripts

- `scripts/flatten-gen.sh`: move `src/**/gen/*` outputs to parent directories, optionally forced and/or dry-run.
- `scripts/prune-identical-src.py`: remove `src/` files that are byte-identical to `orig/` equivalents, then prune empty directories.

Examples:

```bash
./scripts/flatten-gen.sh --dry-run
python3 scripts/prune-identical-src.py --dry-run
```

## Repository layout (high level)

- `src/`: editable mod source content.
- `obj/`: generated intermediate files.
- `out/`: final build output.
- `bin/`: base XEX binaries used by the build.
- `orig/`: reference/original game data for comparisons.
- `tools/`: core build pipeline and bundled platform tools.
- `docs/`: MkDocs documentation source.

## Documentation

Project docs are in `docs/` (MkDocs + Material):

```bash
cd docs
mkdocs serve
```

Then open the local URL shown by MkDocs.

## Contributing

Thanks for your interest in contributing! Please read our guidelines before submitting.

**Quick links:**

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — full guidelines, development workflow, and **AI disclosure policy**
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — community standards and enforcement
- **[SUPPORT.md](SUPPORT.md)** — get help, find resources, report issues

### Key expectations

1. Keep each PR focused on one problem.
2. Avoid unrelated cleanup in the same change.
3. Preserve project scope: this repo is for mod tooling and patch content, not redistribution of proprietary game assets.
4. **If you use AI tools** (GitHub Copilot, ChatGPT, Claude, etc.), disclose it in your PR and verify every change. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
5. Update docs if behavior changes.

### How we handle contributions

- Honest contributions with verified code are welcome.
- Vibe coding, hallucinated explanations, or dishonest AI disclosure will result in **immediate PR rejection and permanent blacklist**.
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for our integrity policy.

## License and legal notice

Original code and original project-authored content in this repository are licensed under the MIT License (see `LICENSE`).

**Important scope limits:**

- Stock/original game assets, data, binaries, names, and other proprietary IP remain the property of their respective rights holders, including Harmonix Music Systems and Epic Games.
- This repository does not grant rights to proprietary game content.
- The project is a non-commercial fan/preservation initiative.
- No copyright infringement is intended.

**Contribution integrity:**
By submitting a contribution, you affirm that you have the right to license it under MIT, that any AI use has been disclosed and verified, and that the code is not hallucinated or unverified. See `LICENSE` for details.

## Credits

- aubmilia
- liningdesert753
- NORXND
- MiloHax community contributors

This project is partially based on [Dance Central 3 Deluxe](https://github.com/hmxmilohax/dance-central-3-deluxe) and includes DataArray language support VS Code plugin from MiloHax.

Special thanks to [MiloHax](https://milohax.org/) for ongoing Milo engine R&D support.
