# Repo Signals

Use repo evidence to classify the project and decide what guidance matters.

## App or service

Signals:
- Web or server manifests such as `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`
- Runtime or deployment files such as Dockerfiles, env examples, migrations, infra config

Usually include:
- How to run locally
- Test, lint, typecheck, build commands
- Env/config caveats
- Migration or deployment safety notes

## Library or SDK

Signals:
- Publish config, package export surfaces, docs/examples, versioning files

Usually include:
- API compatibility expectations
- Example or fixture update expectations
- Release or packaging checks

## CLI

Signals:
- Entry-point scripts, install docs, shell completion, command fixtures

Usually include:
- Local invocation patterns
- Snapshot or help-text verification
- Backward-compatibility notes

## Monorepo

Signals:
- Workspaces, multiple package manifests, `turbo.json`, `pnpm-workspace.yaml`, `nx.json`, multiple services

Usually include:
- Root vs package-level commands
- How to find the correct package
- When nested `AGENTS.md` files should exist

## Infra or platform repo

Signals:
- Terraform, Pulumi, Kubernetes, Helm, deployment workflows, environment folders

Usually include:
- Environment targeting rules
- Plan/apply or dry-run expectations
- Secret and rollout safety rails

## Docs or content repo

Signals:
- MDX/docs generators, content collections, editorial workflows

Usually include:
- Preview/build commands
- Link and formatting checks
- Style or publishing constraints
