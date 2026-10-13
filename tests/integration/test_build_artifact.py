import json
import os
import zipfile
from pathlib import Path


def artifact_path():
    return Path(os.environ.get("BUILD_ARTIFACT", "dist/build.zip"))


def test_staging_environment_and_downloaded_artifact_are_present():
    assert os.environ["TEST_ENV"] == "staging"
    assert artifact_path().is_file()


def test_built_zip_is_complete_and_matches_its_manifest():
    path = artifact_path()

    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        manifest = json.loads(archive.read("manifest.json"))
        readme = archive.read("README.md").decode("utf-8")

    assert manifest["name"] == "devops-readme-automation"
    assert manifest["version"].count(".") == 2
    assert set(manifest["files"]).issubset(names)
    assert "<!-- ACTIVITY:START -->" in readme
    assert "<!-- ACTIVITY:END -->" in readme

