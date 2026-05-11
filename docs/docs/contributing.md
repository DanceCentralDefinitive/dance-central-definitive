# Contributing

## Development expectations

- Keep changes focused and traceable.
- Do not mix unrelated refactors with content edits.
- Update docs for behavioral changes in scripts/tooling.

## Suggested workflow

1. Create a feature branch.
2. Make your change.
3. Run build/test commands relevant to the change.
4. Document what changed and why.
5. Open a pull request with validation notes.

## Validation checklist

- default build succeeds:

```bash
./scripts/build.sh
```

- expanded variant build succeeds:

```bash
./tools/build.py src bin --vanilla --debug
```

- helper scripts behave as expected in dry-run mode:

```bash
./scripts/flatten-gen.sh --dry-run
python3 scripts/prune-identical-src.py --dry-run
```

## Commit guidance

- Prefer concise, descriptive commits.
- Mention impacted paths/components.
- Include migration notes if changing build outputs or flags.

## Attribution

Keep credits and acknowledgements intact when reusing upstream work.
