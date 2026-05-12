# Agent and LLM Instructions

This file defines expectations for AI-assisted changes in this repository.

## Goals

- Produce small, reviewable, deterministic changes.
- Preserve build reproducibility and repository structure.
- Respect legal boundaries around proprietary game content.

## Hard requirements

- Do not rewrite unrelated files.
- Do not perform destructive git operations.
- Do not add binary assets unless explicitly requested.
- Do not introduce new dependencies unless necessary and justified.
- Keep edits in existing style and conventions.

## Change strategy

1. Read relevant files before editing.
2. Prefer minimal diffs over broad refactors.
3. Implement the requested change end to end.
4. Validate with relevant commands.
5. Summarize modified files, behavior changes, and risks.

## Repository-specific guidance

- Main content lives in `src/`.
- Build pipeline entrypoint is `tools/build.py`.
- Helper scripts are in `scripts/`.
- Documentation source is in `docs/`.
- Reference/original content is in `orig/` and should not be treated as freely editable mod output.

## For DTA edits

- Keep symbols and message handlers consistent with nearby patterns.
- Reuse existing runtime helpers where possible.
- Avoid speculative APIs unless explicitly requested.
- If a requested primitive appears unavailable, state the limitation clearly and provide the closest workable approach.

## Validation guidance

Run only checks relevant to the change, for example:

```bash
./scripts/build.sh
./tools/build.py src bin --vanilla --debug
./scripts/flatten-gen.sh --dry-run
python3 scripts/prune-identical-src.py --dry-run
```

## Pull request quality bar

When preparing PR content, include:

- Problem statement
- What changed
- Validation performed
- Limitations and follow-ups

## Communication style

- Be explicit about assumptions.
- Do not claim commands were run if they were not.
- Flag uncertainty instead of guessing.
- Prefer concrete file-level explanations over generic summaries.
