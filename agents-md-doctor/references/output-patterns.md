# Output Patterns

Use the smallest pattern that fits the repo.

## Simple repo

```md
# Repository Guide

## Working Rules
- Short repo-specific rules

## Validation
- Exact commands

## Safety Rails
- What needs confirmation
```

## App or service

```md
# Repository Guide

## Dev Environment Tips
- Local run or bootstrap notes

## Testing Instructions
- Repo and targeted checks

## Safety Rails
- Migrations, env files, deployment-sensitive areas
```

## Library or CLI

```md
# Repository Guide

## Working Rules
- Public API and compatibility expectations

## Validation
- Tests, lint, typecheck, packaging or smoke checks

## Safety Rails
- Breaking changes and release-sensitive files
```

## Monorepo

```md
# Repository Guide

## Dev Environment Tips
- How to find the right package or service
- Root vs package-level commands

## Testing Instructions
- Workspace-wide and package-specific checks

## Nested AGENTS.md
- Where a closer file should override the root guide
```

## Selection rules

- Prefer `Working Rules` + `Validation` + `Safety Rails` for small repos.
- Use `Dev Environment Tips` and `Testing Instructions` when the repo has meaningful setup or CI complexity.
- Add `PR instructions` only if the repo has real title, scope, or merge conventions.
- Add `Review guidelines` only if the repo uses Codex review in GitHub or needs explicit automated review priorities.
- Add nested guidance only for real subproject boundaries.
