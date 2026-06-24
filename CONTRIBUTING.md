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

## AI Use and Integrity Policy

### Disclosure requirement

We welcome contributions that use modern development tools responsibly. **However, AI use must be disclosed honestly.**

When opening a pull request, you **must** complete the "AI Disclosure" section of the PR template. Choose one:

1. **No AI used** — Your work was written, tested, and reviewed entirely without AI tools (GitHub Copilot, ChatGPT, Claude, etc.).
2. **AI used with full accountability** — You used AI tools for parts of this PR, **and you have**:
   - Personally reviewed every change for correctness
   - Tested all modified code paths thoroughly
   - Verified no hallucinations or unintended behavior was introduced
   - Can explain the purpose and mechanics of every change to maintainers
   - Validated that generated code follows project conventions

### What happens if you use AI but don't own it

**Vibe coding, hallucinated explanations, unverified AI output, or dishonest disclosure will result in:**

- ❌ Immediate non-negotiable PR rejection
- ❌ Permanent blacklist from this project and all affiliated projects
- ❌ Notification to collaborating groups and sister projects

**This is not negotiable.** Unverified AI output wastes maintainer time, introduces bugs, and breaks trust. If you cannot honestly verify and explain your changes, do not submit them.

### Why we require this

- **Respect for maintainers** — Reviewing unverified AI output is a burden that slows the project.
- **Code quality** — AI can generate plausible-looking but incorrect code. We need authors who own their changes.
- **Project reputation** — Sneaky contributions reflect poorly on everyone.
- **Your reputation** — Honest disclosure builds trust; dishonesty ends collaboration.

## Legal and licensing

By submitting contributions, you agree your original work is licensed under the repository license unless stated otherwise.
Do not submit content you do not have rights to share.

---

**Questions?** Open a discussion or issue. We're here to help contributors succeed.
