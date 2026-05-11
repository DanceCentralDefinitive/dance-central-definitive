# Troubleshooting

## Build script runs but build fails

Check the terminal for the first failing Ninja rule.

Common causes:

- missing or non-executable binaries under `tools/<platform>/`
- invalid source data syntax (for example `.dta` issues)
- path mistakes in custom includes

## `tools/build.py` does not execute directly on Linux

Verify line endings and executable bit:

```bash
file tools/build.py
chmod +x tools/build.py
```

Then retest:

```bash
./tools/build.py src bin --help
```

## Xenia launch does not start

- confirm `--xenia-path` points to a real executable
- ensure selected XEX exists in `out/`
- reduce `--xenia-args` to isolate bad flags

## Unexpected missing files in `src/`

If you ran pruning/flatten scripts, rerun with `--dry-run` first next time.

Recovery options:

- restore from git history
- restore from backup copy
- re-extract from `orig/` baseline

## Docs preview does not start

Install dependencies in your active Python environment:

```bash
pip install mkdocs mkdocs-material
```

Then run:

```bash
cd docs
mkdocs serve
```
