---
name: agents-md-doctor
description: Review a repository, infer its working conventions, and draft or refresh a concise repo-specific AGENTS.md with exact commands, workflow rules, validation steps, and safety rails. Use when Codex is asked to create, rewrite, tighten, audit, or modernize AGENTS.md or similar repo instruction files using repository evidence plus the official AGENTS.md examples.
---

# AGENTS.md Doctor

Produce short, evidence-based `AGENTS.md` files. Treat the OpenAI Codex `AGENTS.md` docs and the official `agents.md` examples as pattern sources, then adapt them to the actual repo instead of copying generic advice.

## Quick start

1. Ask one focused question for repo type: app, API/service, library, CLI, monorepo, infra, docs/content, mobile, or mixed.
2. Read [references/official-examples.md](./references/official-examples.md).
3. Run `python3 scripts/repo_inventory.py <repo-root>` to collect manifests, likely validation commands, CI files, workspace hints, docs signals, and existing instruction files.
4. Inspect the highest-signal files the inventory finds.
5. Draft a short `AGENTS.md` using [references/output-patterns.md](./references/output-patterns.md) and [references/repo-signals.md](./references/repo-signals.md).

## Source of truth

1. Current OpenAI Codex docs for `AGENTS.md` and Codex review behavior
2. Actual repository files and commands
3. Existing `AGENTS.md`, `AGENTS.override.md`, and fallback instruction files
4. Current official examples at `https://agents.md/#examples`
5. Bundled references in this skill as helper context only

If browsing is available, check the current OpenAI Codex docs and the current official examples before finalizing. If not, use the bundled reference and continue.

## Workflow

1. Classify the repo type from the user's answer plus repo evidence. If they disagree, call that out and prefer codebase evidence.
2. Use the inventory script first. It is intentionally bounded-depth and time-bounded for speed, so if it reports a truncated scan or the repo structure clearly needs it, inspect deeper paths manually. Use it to surface common package-manager hints, key validation commands, non-GitHub CI files, docs-heavy repos, and existing guidance before you inspect anything manually. Then inspect only the files needed to confirm package manager, test/lint/build/typecheck commands, workspace layout, CI entry points, deployment-sensitive files, and existing agent guidance.
3. Infer conventions only from evidence. Never invent commands, directory names, review rules, or architecture constraints.
4. Borrow section shapes from the official examples when they fit. Typical sections: `Dev environment tips`, `Testing instructions`, `PR instructions`, `Review guidelines`, and nested `AGENTS.md` guidance for monorepos.
5. Keep the output tight. Default to one root `AGENTS.md` under about 60 lines. Add nested guidance only when the repo clearly has distinct subprojects with different commands or rules.
6. Preserve high-signal existing constraints. Remove fluff, duplicated defaults, stale advice, and generic slogans.
7. Make validation explicit. Every generated file should include exact pre-handoff checks that exist in the repo.
8. When nested overrides are needed, prefer `AGENTS.override.md` close to the specialized work. Remember that same-directory `AGENTS.override.md` wins over `AGENTS.md`, and the closest matching file applies to changed files.

## Output contract

Always produce a practical file, usually with this minimum shape:

```md
# Repository Guide

## Working Rules
- Repo-specific workflow rules

## Validation
- Exact commands to run

## Safety Rails
- Actions that need confirmation or extra care
```

Expand only when the repo evidence supports it. Prefer exact commands and paths over prose.

## Reference map

- [references/official-examples.md](./references/official-examples.md): distilled guidance from the official `agents.md` examples and usage notes
- [references/repo-signals.md](./references/repo-signals.md): repo-type detection cues and what guidance each repo type usually needs
- [references/output-patterns.md](./references/output-patterns.md): concise output shapes for simple repos, services, libraries, and monorepos

## Quality rules

- Treat official `agents.md` examples as pattern guidance, not copy to paste.
- Treat the OpenAI Codex docs as source-of-truth behavior for precedence, fallback filenames, and Codex review behavior.
- Treat repo files as the source of truth for commands and conventions.
- Prefer the smallest useful file over a comprehensive handbook.
- If a command cannot be verified, remove it or mark it unconfirmed.
- If the repo lacks evidence for a rule, omit it.
- Flag uncertainty when repo type, tooling, or existing instructions conflict.
- Ask before adding guidance for destructive operations, production changes, migrations, secret rotation, or new dependencies unless the repo already standardizes them.
- Add `Review guidelines` only when the repo clearly uses Codex reviews in GitHub or has explicit automated review priorities worth encoding.

## Tooling notes

- Use the inventory script before broad manual searching.
- Check OpenAI Codex docs for `AGENTS.md` precedence, fallback filenames, and review-specific behavior when those details matter.
- Browse `https://agents.md/#examples` when available for current example patterns.
- For monorepos, mention nested `AGENTS.md` precedence only when package or service boundaries are real in the repo.
