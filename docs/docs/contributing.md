# Contributing

Use this page as a quick contributor checklist. For full repository guidance, see the root `CONTRIBUTING.md`.

## Workflow

1. Create a focused branch for one logical change.
2. Implement the smallest reasonable fix or feature.
3. Run validation relevant to your touched areas.
4. Update docs if behavior or workflow changed.
5. Open a pull request using `.github/PULL_REQUEST_TEMPLATE.md`.

## Validation commands

```bash
./scripts/build.sh
./tools/build.py src bin --vanilla --debug
./scripts/flatten-gen.sh --dry-run
python3 scripts/prune-identical-src.py --dry-run
```

Run what applies to your change and report exactly what you executed.

## Pull request expectations

- State what changed and why.
- Include validation commands and outcomes.
- Note limitations, risk, and follow-up work.
- Keep unrelated refactors out of the same PR.

## AI-assisted contributions

If you use AI tools, follow `AGENTS.md` to keep edits minimal, reviewable, and safe.
