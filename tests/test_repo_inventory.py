from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "agents-md-doctor" / "scripts" / "repo_inventory.py"


def run_inventory(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args, str(repo_root)],
        check=True,
        capture_output=True,
        text=True,
    )


class RepoInventoryTests(unittest.TestCase):
    def test_docs_heavy_repo_with_helper_script_is_docs_or_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "SKILL.md").write_text("# Skill\n")
            (root / "references").mkdir()
            (root / "references" / "guide.md").write_text("# Guide\n")
            (root / "notes").mkdir()
            (root / "notes" / "usage.md").write_text("# Usage\n")
            (root / "scripts").mkdir()
            (root / "scripts" / "repo_inventory.py").write_text("print('hi')\n")

            result = run_inventory(root, "--json")
            summary = json.loads(result.stdout)

            self.assertEqual(summary["likely_repo_type"], "docs-or-content")
            self.assertIn(str((root / "scripts" / "repo_inventory.py").resolve()), summary["script_files"])

    def test_python_marker_files_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "requirements.txt").write_text("pytest\n")
            (root / "scripts").mkdir()
            (root / "scripts" / "run.py").write_text("print('hi')\n")

            result = run_inventory(root, "--json")
            summary = json.loads(result.stdout)

            self.assertEqual(summary["likely_repo_type"], "service-or-library")
            self.assertIn(str((root / "requirements.txt").resolve()), summary["python_project_files"])

    def test_render_includes_key_scripts_and_non_github_ci(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "scripts": {
                            "dev": "vite",
                            "test": "vitest run",
                            "lint": "eslint .",
                        },
                    }
                )
            )
            (root / ".gitlab-ci.yml").write_text("stages: [test]\n")

            result = run_inventory(root)

            self.assertIn('key=dev="vite", test="vitest run", lint="eslint ."', result.stdout)
            self.assertIn("CI workflows:\n- .gitlab-ci.yml", result.stdout)

    def test_monorepo_with_workspace_markers_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pnpm-workspace.yaml").write_text("packages:\n  - packages/*\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True, "workspaces": ["packages/*"]})
            )
            (root / "packages" / "app").mkdir(parents=True)
            (root / "packages" / "lib").mkdir(parents=True)
            (root / "packages" / "app" / "package.json").write_text(json.dumps({"name": "@demo/app"}))
            (root / "packages" / "lib" / "package.json").write_text(json.dumps({"name": "@demo/lib"}))

            result = run_inventory(root, "--json")
            summary = json.loads(result.stdout)

            self.assertEqual(summary["likely_repo_type"], "monorepo")
            self.assertIn(str((root / "pnpm-workspace.yaml").resolve()), summary["workspace_markers"])
            self.assertEqual(len(summary["package_json"]), 3)

    def test_terraform_only_repo_is_detected_as_infra(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "infra").mkdir()
            (root / "infra" / "main.tf").write_text('terraform { required_version = ">= 1.6.0" }\n')
            (root / "infra" / "terraform.tfvars").write_text('environment = "prod"\n')

            result = run_inventory(root, "--json")
            summary = json.loads(result.stdout)

            self.assertEqual(summary["likely_repo_type"], "infra")
            self.assertIn(str((root / "infra" / "main.tf").resolve()), summary["infra_files"])


if __name__ == "__main__":
    unittest.main()
