# AGENTS.md Doctor

[![CI](https://github.com/daniel-p-green/codex-skill_secret-agents-dot-md-doctor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/daniel-p-green/codex-skill_secret-agents-dot-md-doctor/actions/workflows/ci.yml)

`agents-md-doctor` is a Codex skill for drafting or refreshing short, repo-specific `AGENTS.md` files from actual repository evidence.

The goal is to produce operational guidance that helps Codex work correctly in a repo without turning `AGENTS.md` into a handbook. The skill starts from repository facts, not generic advice, and uses current OpenAI Codex guidance plus the public `agents.md` examples as pattern inputs.

## What it does

- Classifies a repository from lightweight signals such as manifests, workspace markers, CI files, docs structure, infra files, and instruction files.
- Surfaces high-signal facts with `agents-md-doctor/scripts/repo_inventory.py` before deeper manual inspection.
- Drafts concise `AGENTS.md` files with exact commands, validation steps, workflow rules, and safety rails.
- Preserves repo-specific constraints while stripping stale or generic filler.
- Supports nested instruction layouts when a monorepo or multi-surface repo actually needs them, including `AGENTS.override.md` where appropriate.

## Source of truth

Use sources in this order:

1. Current OpenAI Codex docs
2. Actual repository files and commands
3. Existing `AGENTS.md`, `AGENTS.override.md`, and configured fallback instruction files
4. Current [agents.md examples](https://agents.md/#examples)
5. Bundled references in this repo as local fallback context

## OpenAI behaviors this skill accounts for

This skill now explicitly tracks the OpenAI Codex `AGENTS.md` behavior described in the official docs:

- The closest applicable instructions file should drive behavior for changed files.
- `AGENTS.override.md` in a directory wins over `AGENTS.md` in that same directory.
- Fallback instruction filenames can be configured, with OpenAI docs showing `TEAM_GUIDE.md` and `.agents.md` as examples.
- Codex review behavior in GitHub can be tuned with a `Review guidelines` section in `AGENTS.md`.

Primary references:

- [OpenAI Codex: Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [OpenAI Codex: Customize what Codex reviews](https://developers.openai.com/codex/integrations/github#customize-what-codex-reviews)
- [agents.md examples](https://agents.md/#examples)

## How it works

1. Read the skill guidance in [agents-md-doctor/SKILL.md](./agents-md-doctor/SKILL.md).
2. Run the inventory script against a target repo.
3. Inspect only the highest-signal files the inventory surfaces.
4. Draft the smallest useful `AGENTS.md` for that repo shape.
5. Add nested overrides only when the repo has real subproject boundaries or review-specific needs.

## What good output looks like

- Small by default. A short root `AGENTS.md` is usually enough.
- Operational, not aspirational. Prefer exact commands, paths, and review rules over broad advice.
- Repo-specific. If a rule is not grounded in the codebase or current Codex docs, leave it out.
- Verifiable. Every draft should make the expected checks explicit.
- Layered only when needed. Put specialized overrides close to the work they govern.

## Repository layout

- [agents-md-doctor/SKILL.md](./agents-md-doctor/SKILL.md): skill instructions and workflow.
- [agents-md-doctor/scripts/repo_inventory.py](./agents-md-doctor/scripts/repo_inventory.py): bounded repo signal scanner used to bootstrap drafting.
- [agents-md-doctor/references/official-examples.md](./agents-md-doctor/references/official-examples.md): local fallback summary of official patterns and OpenAI-specific behaviors.
- [agents-md-doctor/references/output-patterns.md](./agents-md-doctor/references/output-patterns.md): minimal file shapes for simple repos, services, libraries, and monorepos.
- [agents-md-doctor/references/repo-signals.md](./agents-md-doctor/references/repo-signals.md): repo classification cues.
- [agents-md-doctor/agents/openai.yaml](./agents-md-doctor/agents/openai.yaml): interface metadata.
- [tests/test_repo_inventory.py](./tests/test_repo_inventory.py): behavior tests for the inventory heuristics.

## Inventory script

Run the scanner from the repo root:

```bash
python3 agents-md-doctor/scripts/repo_inventory.py <repo-root>
python3 agents-md-doctor/scripts/repo_inventory.py --json <repo-root>
```

The scanner is intentionally bounded for speed:

- depth-limited
- file-count limited
- time-bounded

It is meant to narrow the search space, not replace manual inspection.

## Verify against live Codex

The current Codex docs recommend verifying instruction loading directly:

```bash
codex --ask-for-approval never "Summarize the current instructions."
codex --cd <subdir> --ask-for-approval never "Show which instruction files are active."
```

Use those checks to confirm:

- root guidance is loaded in precedence order
- nested overrides replace broader rules when expected
- no stale assumptions are being carried between runs

If instruction loading looks wrong, restart Codex in the target directory. The Codex docs note that the instruction chain is rebuilt on each run and at the start of each TUI session.

## Local development

Validation commands for this repo:

```bash
python3 -m unittest discover -s tests
python3 -m py_compile agents-md-doctor/scripts/repo_inventory.py tests/test_repo_inventory.py
python3 agents-md-doctor/scripts/repo_inventory.py .
```

## Current coverage

The current tests cover:

- docs-heavy skill-style repos
- Python marker detection without a full `pyproject.toml`
- key script and CI rendering from `package.json`
- monorepo detection from workspace markers and multiple package manifests
- infra-only detection from Terraform files

## When to update this skill

The Codex customization docs give good triggers for changing `AGENTS.md` guidance. Update this skill when you see the same patterns here:

- repeated drafting mistakes that should become explicit rules
- too much file reading before the right repo signals are found
- recurring review feedback on generated `AGENTS.md` files
- missing enforcement hooks between guidance and actual checks

In practice, that usually means adjusting the inventory heuristics, tightening the drafting rules in `SKILL.md`, or expanding the local references to reflect new Codex behavior.

## Constraints

- The inventory script is heuristic-based and should not invent commands or conventions.
- The final `AGENTS.md` should stay short unless the repo clearly justifies more structure.
- `Review guidelines` should be added only when the repo uses Codex review workflows or has explicit automated review priorities worth encoding.
- This README is for humans. The executable workflow lives in `agents-md-doctor/SKILL.md`.
