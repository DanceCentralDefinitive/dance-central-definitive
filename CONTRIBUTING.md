# Contributing to Dance Central Definitive

Thanks for helping improve this project.

## Before you start

- Keep each pull request focused on one problem.
- Avoid unrelated cleanup in the same change.
- Preserve project scope: this repo is for mod tooling and patch content, not redistribution of proprietary game assets.
- Read project docs in `docs/` if you are touching build or workflow behavior.

## Development workflow

1. Fork and create a branch with a clear name.
2. Implement the smallest reasonable change.
3. Validate locally.
4. Update docs if behavior, flags, outputs, or workflows changed.
5. Open a pull request using the provided template.

## Validation

Run the checks relevant to your change.

### Default build

```bash
./scripts/build.sh
```

### Expanded build variant

```bash
./tools/build.py src bin --vanilla --debug
```

### Script dry-run checks

```bash
./scripts/flatten-gen.sh --dry-run
python3 scripts/prune-identical-src.py --dry-run
```

## Content and code expectations

- Match existing style and naming in touched files.
- Do not move or rename files without a reason described in the PR.
- Keep generated output out of commits unless the change explicitly requires tracked generated artifacts.
- Add brief comments only where logic is not obvious.

## Commit guidance

- Use descriptive commits that explain intent.
- Mention impacted areas (for example: build pipeline, DTA screen flow, docs).
- Include migration notes in commit or PR text when changing build outputs or flags.

## Pull request expectations

- Explain what changed and why.
- Include test and validation steps you actually ran.
- Note any limitations, follow-ups, or known risks.
- Add screenshots or logs where useful.

## Legal and licensing

By submitting contributions, you agree your original work is licensed under the repository license unless stated otherwise.

Do not submit content you do not have rights to share.
