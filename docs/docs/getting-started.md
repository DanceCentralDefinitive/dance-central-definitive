# Getting Started

## Prerequisites

- Python 3.11+
- Bash (Linux/macOS) or `cmd.exe` (Windows)
- Execute permission for platform tools in `tools/<platform>/`
- Source content in `src/`
- Base binaries in `bin/`

Optional for docs work:

- MkDocs + Material theme (`mkdocs`, `mkdocs-material`)

## First build

From repository root:

```bash
./scripts/build.sh
```

On Windows:

```bat
scripts\build.bat
```

Expected result:

- A generated `build.ninja`
- Intermediate files in `obj/`
- Final output in `out/`

## Verify tool entrypoint

```bash
./tools/build.py src bin --help
```

If this works, your Python/tooling path is healthy.

## Optional: run docs locally

```bash
cd docs
mkdocs serve
```

MkDocs prints a local URL. Open it to preview docs changes.

## Typical next step

Build all major variants:

```bash
./tools/build.py src bin --vanilla --debug
```
