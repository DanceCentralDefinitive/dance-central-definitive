# Modding Workflow

## Source and generated paths

- Edit source content under `src/`
- Build intermediates are generated in `obj/`
- Final build artifacts are emitted into `out/`

Do not manually edit generated files inside `obj/`.

## Recommended iteration loop

1. Change data/assets in `src/`.
2. Run build.
3. Inspect output in `out/`.
4. Test in emulator/hardware setup.
5. Repeat.

## Managing generated `gen` folders

When conversion output lands in nested `gen` directories and you need to flatten paths, use:

```bash
./scripts/flatten-gen.sh --dry-run
./scripts/flatten-gen.sh
```

Use `--force` to overwrite collisions.

## Pruning unchanged source files

To remove files from `src/` that are byte-identical to `orig/`:

```bash
python3 scripts/prune-identical-src.py --dry-run
python3 scripts/prune-identical-src.py
```

This keeps your mod source tree focused on real deltas.

## Safety notes

- Prefer dry-runs before destructive scripts.
- Keep `orig/` untouched as a reference baseline.
- Commit in small, reviewable chunks.
