#!/usr/bin/env python3
"""Collect high-signal repo facts for AGENTS.md drafting."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


IGNORE_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    ".yarn",
    ".pnpm-store",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "venv",
    "vendor",
    "target",
    "tmp",
    "out",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".idea",
    ".vscode",
    "__pycache__",
}

FALLBACK_INSTRUCTION_FILES = ("TEAM_GUIDE.md", ".agents.md")
MARKDOWN_EXTENSIONS = {".md", ".mdx"}
README_FILES = {"README", "README.md", "README.mdx", "readme.md", "readme.mdx"}
PYTHON_PROJECT_MARKERS = {
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "uv.lock",
    "poetry.lock",
    "Pipfile",
    "setup.py",
    "setup.cfg",
    "tox.ini",
    "pytest.ini",
}
SCRIPT_DIR_NAMES = {"bin", "scripts", "tools"}
SCRIPT_EXTENSIONS = {".py", ".sh", ".bash", ".zsh", ".ps1", ".js", ".mjs", ".cjs", ".ts", ".rb"}
KEY_SCRIPT_NAMES = ("dev", "start", "build", "test", "test:ci", "lint", "typecheck", "check", "verify", "format")
CI_FILE_NAMES = {"Jenkinsfile", ".gitlab-ci.yml", ".travis.yml", "azure-pipelines.yml", "bitbucket-pipelines.yml"}
CI_PATH_SUFFIXES = {(".circleci", "config.yml"), (".buildkite", "pipeline.yml")}
MAX_DEPTH = 6
MAX_FILES = 8000
MAX_SECONDS = 3.0


def safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text()
    except (OSError, UnicodeDecodeError):
        return None


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_package_json(path: Path) -> dict:
    data = json.loads(path.read_text())
    scripts = data.get("scripts") or {}
    return {
        "path": str(path),
        "name": data.get("name"),
        "packageManager": data.get("packageManager"),
        "scripts": sorted(scripts.keys()),
        "key_scripts": pick_key_scripts(scripts),
        "workspaces": bool(data.get("workspaces")),
    }


def parse_pyproject(path: Path) -> dict:
    if tomllib is None:
        return {"path": str(path), "error": "tomllib unavailable"}
    data = tomllib.loads(path.read_text())
    project = data.get("project", {})
    scripts = sorted((project.get("scripts") or {}).keys())
    return {
        "path": str(path),
        "name": project.get("name"),
        "scripts": scripts,
        "has_poetry": "poetry" in data.get("tool", {}),
        "has_pytest": "pytest" in data.get("tool", {}),
    }


def parse_cargo(path: Path) -> dict:
    if tomllib is None:
        return {"path": str(path), "error": "tomllib unavailable"}
    data = tomllib.loads(path.read_text())
    return {
        "path": str(path),
        "package": (data.get("package") or {}).get("name"),
        "workspace": "workspace" in data,
    }


def parse_make_like(path: Path) -> list[str]:
    text = safe_read_text(path) or ""
    targets = []
    for line in text.splitlines():
        if line.startswith("\t") or line.startswith(" ") or ":" not in line:
            continue
        name = line.split(":", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z0-9_.@%/+:-]+", name):
            targets.append(name)
    return sorted(set(targets))


def pick_key_scripts(scripts: dict[str, str]) -> dict[str, str]:
    selected = {}
    for name in KEY_SCRIPT_NAMES:
        command = scripts.get(name)
        if isinstance(command, str):
            selected[name] = command
    if selected:
        return selected
    for name in sorted(scripts)[:5]:
        command = scripts.get(name)
        if isinstance(command, str):
            selected[name] = command
    return selected


def is_ci_file(path: Path) -> bool:
    if path.name in CI_FILE_NAMES:
        return True
    return tuple(path.parts[-2:]) in CI_PATH_SUFFIXES


def is_script_entry(path: Path) -> bool:
    in_script_dir = any(part in SCRIPT_DIR_NAMES for part in path.parts)
    if not in_script_dir:
        return False
    return path.suffix.lower() in SCRIPT_EXTENSIONS or path.suffix == ""


def format_key_scripts(scripts: dict[str, str]) -> str:
    return ", ".join(f'{name}="{command}"' for name, command in scripts.items())


def walk_files(root: Path):
    for current_root, dirnames, filenames in os.walk(root, topdown=True):
        relative_parts = Path(current_root).relative_to(root).parts
        depth = len(relative_parts)
        if depth >= MAX_DEPTH:
            dirnames[:] = []
        else:
            dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        current_path = Path(current_root)
        for filename in filenames:
            yield current_path / filename


def detect_repo_type(summary: dict) -> str:
    has_manifest_code = any(
        [
            summary["package_json"],
            summary["pyproject"],
            summary["cargo_toml"],
            summary["go_mod"],
            summary["python_project_files"],
        ]
    )
    has_script_entry = bool(summary["script_files"])
    has_markdown_content = bool(summary["markdown_files"] or summary["readme_files"])

    if summary["workspace_markers"] or len(summary["package_json"]) > 1:
        return "monorepo"
    if summary["infra_files"] and (has_manifest_code or has_script_entry):
        return "mixed"
    if summary["infra_files"]:
        return "infra"
    if has_manifest_code:
        return "service-or-library"
    if has_markdown_content and len(summary["markdown_files"]) >= 3:
        return "docs-or-content"
    if has_script_entry:
        return "service-or-library"
    return "unknown"


def build_summary(root: Path) -> dict:
    started = time.monotonic()
    files = []
    truncated = False
    for path in walk_files(root):
        files.append(path)
        if len(files) >= MAX_FILES or (time.monotonic() - started) >= MAX_SECONDS:
            truncated = True
            break
    package_json = []
    pyproject = []
    cargo_toml = []
    go_mod = []
    makefiles = []
    justfiles = []
    ci_files = []
    instruction_files = []
    docker_files = []
    infra_files = []
    docs_files = []
    markdown_files = []
    python_project_files = []
    readme_files = []
    script_files = []
    workspace_markers = []

    for path in files:
        if path.is_dir():
            continue
        name = path.name
        if path.suffix.lower() in MARKDOWN_EXTENSIONS:
            markdown_files.append(str(path))
        if name in README_FILES:
            readme_files.append(str(path))
        if is_script_entry(path):
            script_files.append(str(path))
        if name == "package.json":
            package_json.append(parse_package_json(path))
        elif name == "pyproject.toml":
            pyproject.append(parse_pyproject(path))
        elif name == "Cargo.toml":
            cargo_toml.append(parse_cargo(path))
        elif name == "go.mod":
            go_mod.append({"path": str(path), "module": (safe_read_text(path) or "").splitlines()[:1]})
        elif name in PYTHON_PROJECT_MARKERS:
            python_project_files.append(str(path))
        elif name in {"Makefile", "makefile"}:
            makefiles.append({"path": str(path), "targets": parse_make_like(path)[:20]})
        elif name == "justfile":
            justfiles.append({"path": str(path), "targets": parse_make_like(path)[:20]})
        elif is_ci_file(path) or ".github/workflows/" in str(path):
            ci_files.append(str(path))
        elif name in {"AGENTS.md", "AGENTS.override.md", *FALLBACK_INSTRUCTION_FILES}:
            instruction_files.append(str(path))
        elif name.startswith("Dockerfile") or name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            docker_files.append(str(path))
        elif path.suffix in {".tf", ".tfvars"} or "k8s" in path.parts or "helm" in path.parts:
            infra_files.append(str(path))
        elif path.suffix.lower() in MARKDOWN_EXTENSIONS and any(part in {"docs", "content"} for part in path.parts):
            docs_files.append(str(path))
        elif name in {"pnpm-workspace.yaml", "turbo.json", "nx.json", "lerna.json"}:
            workspace_markers.append(str(path))

    summary = {
        "root": str(root),
        "truncated": truncated,
        "package_json": package_json,
        "pyproject": pyproject,
        "cargo_toml": cargo_toml,
        "go_mod": go_mod,
        "python_project_files": sorted(python_project_files),
        "makefiles": makefiles,
        "justfiles": justfiles,
        "ci_files": sorted(ci_files),
        "instruction_files": sorted(instruction_files),
        "docker_files": sorted(docker_files),
        "infra_files": sorted(infra_files),
        "docs_files": sorted(docs_files[:20]),
        "markdown_files": sorted(markdown_files[:20]),
        "readme_files": sorted(readme_files),
        "script_files": sorted(script_files[:20]),
        "workspace_markers": sorted(workspace_markers),
    }
    summary["likely_repo_type"] = detect_repo_type(summary)
    return summary


def render(summary: dict, root: Path) -> str:
    lines = [
        f"Root: {summary['root']}",
        f"Likely repo type: {summary['likely_repo_type']}",
    ]
    if summary.get("truncated"):
        lines.append("Scan truncated: yes (inspect deeper manually if key signals are missing)")
    if summary["workspace_markers"]:
        lines.append("Workspace markers:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["workspace_markers"])
    if summary["package_json"]:
        lines.append("package.json files:")
        for item in summary["package_json"][:10]:
            line = f"- {rel(root, Path(item['path']))}: scripts={', '.join(item['scripts']) or '(none)'}"
            if item["key_scripts"]:
                line += f"; key={format_key_scripts(item['key_scripts'])}"
            lines.append(line)
    if summary["pyproject"]:
        lines.append("pyproject.toml files:")
        for item in summary["pyproject"][:10]:
            lines.append(
                f"- {rel(root, Path(item['path']))}: scripts={', '.join(item['scripts']) or '(none)'}"
            )
    if summary["python_project_files"]:
        lines.append("Python project files:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["python_project_files"][:20])
    if summary["cargo_toml"]:
        lines.append("Cargo.toml files:")
        for item in summary["cargo_toml"][:10]:
            lines.append(f"- {rel(root, Path(item['path']))}: workspace={item['workspace']}")
    if summary["makefiles"]:
        lines.append("Makefiles:")
        for item in summary["makefiles"][:10]:
            lines.append(
                f"- {rel(root, Path(item['path']))}: targets={', '.join(item['targets'][:12]) or '(none)'}"
            )
    if summary["justfiles"]:
        lines.append("justfiles:")
        for item in summary["justfiles"][:10]:
            lines.append(
                f"- {rel(root, Path(item['path']))}: targets={', '.join(item['targets'][:12]) or '(none)'}"
            )
    if summary["ci_files"]:
        lines.append("CI workflows:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["ci_files"][:20])
    if summary["instruction_files"]:
        lines.append("Instruction files:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["instruction_files"][:20])
    if summary["readme_files"]:
        lines.append("Readme files:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["readme_files"][:20])
    if summary["script_files"]:
        lines.append("Script entry points:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["script_files"][:20])
    if summary["likely_repo_type"] == "docs-or-content" and summary["markdown_files"]:
        lines.append("Markdown files:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["markdown_files"][:20])
    if summary["docker_files"]:
        lines.append("Container files:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["docker_files"][:20])
    if summary["infra_files"]:
        lines.append("Infra files:")
        lines.extend(f"- {rel(root, Path(item))}" for item in summary["infra_files"][:20])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize repo signals for AGENTS.md drafting.")
    parser.add_argument("repo_root", nargs="?", default=".", help="Path to repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    summary = build_summary(root)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(render(summary, root), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
