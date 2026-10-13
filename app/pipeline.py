"""Build and validate the README automation release artifact."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Sequence

START_MARKER = "<!-- ACTIVITY:START -->"
END_MARKER = "<!-- ACTIVITY:END -->"
REQUIRED_FILES = (
    "README.md",
    ".github/workflows/update-readme.yml",
    ".github/workflows/validate-readme.yml",
    ".github/workflows/deployment-pipeline.yml",
    "app/pipeline.py",
    "scripts/build.py",
)
VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+\Z")


def extract_activity_section(readme: str) -> str:
    """Return the text between the single, correctly ordered activity markers."""
    if readme.count(START_MARKER) != 1:
        raise ValueError("README must contain exactly one ACTIVITY:START marker")
    if readme.count(END_MARKER) != 1:
        raise ValueError("README must contain exactly one ACTIVITY:END marker")

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)
    if start >= end:
        raise ValueError("README activity markers are in the wrong order")

    section = readme[start:end].strip()
    if not section:
        raise ValueError("README activity section must not be empty")
    return section


def validate_repository(repo_root: Path) -> tuple[str, list[str]]:
    """Check release inputs and README markers before packaging."""
    root = Path(repo_root)
    missing = [path for path in REQUIRED_FILES if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError("Missing required files: " + ", ".join(missing))

    readme = (root / "README.md").read_text(encoding="utf-8")
    extract_activity_section(readme)
    return readme, list(REQUIRED_FILES)


def build_package(repo_root: Path, output_path: Path, version: str) -> Path:
    """Create the ZIP artifact consumed by all downstream deployment jobs."""
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("Version must use the numeric MAJOR.MINOR.PATCH format")

    root = Path(repo_root)
    _readme, files = validate_repository(root)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": "devops-readme-automation",
        "version": version,
        "test_environments": ["staging", "prod"],
        "files": files,
    }

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative_path in files:
            archive.write(root / relative_path, arcname=relative_path)
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )
    return output


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the deployment ZIP artifact")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output", type=Path, default=Path("dist/build.zip"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args(argv)

    output = build_package(args.repo_root, args.output, args.version)
    print(f"Build artifact created: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

