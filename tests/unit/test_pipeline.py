import json
import zipfile

import pytest

from app.pipeline import (
    END_MARKER,
    REQUIRED_FILES,
    START_MARKER,
    build_package,
    extract_activity_section,
    main,
    validate_repository,
)


def make_repo(tmp_path, *, missing=()):
    root = tmp_path / "repo"
    for relative_path in REQUIRED_FILES:
        if relative_path in missing:
            continue
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if relative_path == "README.md":
            file_path.write_text(
                f"# Demo\n{START_MARKER}\n## Latest Commits\n{END_MARKER}\n",
                encoding="utf-8",
            )
        else:
            file_path.write_text("# workflow or build source\n", encoding="utf-8")
    return root


def test_extract_activity_section_returns_only_marked_content():
    readme = f"before\n{START_MARKER}\nlatest commits\n{END_MARKER}\nafter"

    assert extract_activity_section(readme) == "latest commits"


@pytest.mark.parametrize(
    "readme, message",
    [
        ("no markers", "exactly one ACTIVITY:START"),
        (f"{START_MARKER}\n{START_MARKER}\n{END_MARKER}", "exactly one ACTIVITY:START"),
        (f"{END_MARKER}\n{START_MARKER}\nactivity", "wrong order"),
        (f"{START_MARKER}\n{END_MARKER}", "must not be empty"),
    ],
)
def test_extract_activity_section_rejects_invalid_markers(readme, message):
    with pytest.raises(ValueError, match=message):
        extract_activity_section(readme)


def test_validate_repository_checks_required_workflows(tmp_path):
    root = make_repo(tmp_path)

    readme, files = validate_repository(root)

    assert "## Latest Commits" in readme
    assert files == list(REQUIRED_FILES)


def test_validate_repository_reports_missing_inputs(tmp_path):
    root = make_repo(tmp_path, missing=(".github/workflows/update-readme.yml",))

    with pytest.raises(FileNotFoundError, match="update-readme.yml"):
        validate_repository(root)


def test_build_package_writes_manifest_and_workflow_sources(tmp_path):
    root = make_repo(tmp_path)
    output = tmp_path / "nested" / "build.zip"

    result = build_package(root, output, "1.2.3")

    assert result == output
    with zipfile.ZipFile(output) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["version"] == "1.2.3"
        assert manifest["test_environments"] == ["staging", "prod"]
        assert set(manifest["files"]).issubset(archive.namelist())


def test_build_package_rejects_non_numeric_version(tmp_path):
    root = make_repo(tmp_path)

    with pytest.raises(ValueError, match="MAJOR.MINOR.PATCH"):
        build_package(root, tmp_path / "build.zip", "latest")


def test_cli_entry_point_builds_artifact(tmp_path):
    root = make_repo(tmp_path)
    output = tmp_path / "cli" / "build.zip"

    assert main(["--repo-root", str(root), "--output", str(output), "--version", "2.4.6"]) == 0
    assert output.is_file()

