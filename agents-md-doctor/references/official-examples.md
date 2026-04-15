# Official Example Guidance

Use this file as the local fallback when live browsing is unavailable.

OpenAI Codex docs to verify against when browsing is available:
- `https://developers.openai.com/codex/guides/agents-md`
- `https://developers.openai.com/codex/integrations/github#customize-what-codex-reviews`

## What the official examples emphasize

- Keep `AGENTS.md` operational: setup, testing, review, and safety details that help an agent execute work.
- Prefer exact commands over abstract advice.
- Include only conventions that are specific enough to change behavior.
- Use nested `AGENTS.md` files in large monorepos so the closest file can specialize subproject behavior.
- Prefer small files. OpenAI docs explicitly note that a small `AGENTS.md` is often enough.
- Same-directory `AGENTS.override.md` wins over `AGENTS.md`.
- For changed files, the closest applicable instructions file is what matters.

## Common section shapes

- `Dev environment tips`
  - Fast navigation commands
  - Workspace-specific install or bootstrap commands
  - How to find the right package or app
- `Testing instructions`
  - Where CI lives
  - Canonical repo-level and package-level checks
  - Focused test commands
  - Expectation to leave changed code covered and passing
- `PR instructions`
  - Title or scope conventions
  - Required checks before commit or merge
  - Repo-specific review expectations
- `Review guidelines`
  - Priorities Codex should enforce during review
  - Security or correctness checks that should be treated as high severity
  - Repo-specific review focus beyond the default GitHub review behavior

## Usage notes from the official site

- There are no required fields; `AGENTS.md` is plain Markdown.
- Popular content includes project overview, build/test commands, code style, testing instructions, and security considerations.
- Extra agent-facing instructions that do not belong in a human README are fair game.
- Nested `AGENTS.md` files are recommended for large monorepos with distinct subprojects.
- The closest `AGENTS.md` in the directory tree wins when multiple files apply.
- When `AGENTS.override.md` exists in a directory, it overrides `AGENTS.md` in that directory.
- Codex stops searching once it reaches the current working directory, so place overrides close to specialized work.
- Fallback filenames can be configured. OpenAI docs show `TEAM_GUIDE.md` and `.agents.md` as fallback examples.
- OpenAI docs show discovery order within a directory as `AGENTS.override.md`, `AGENTS.md`, then configured fallback filenames.
- In GitHub, Codex flags only P0 and P1 issues by default. If a repo wants broader review coverage, encode that in `Review guidelines`.

## Adaptation rules

- Copy structure, not wording.
- Replace placeholders with real repo terms and commands.
- Collapse sections when the repo is simple.
- Skip example-specific tooling that does not match the codebase.
- Add `Review guidelines` only when the repo actually uses Codex review workflows or needs explicit automated review priorities.
