import json
import os
import zipfile
from pathlib import Path


def test_production_smoke_checks_promoted_build():
    assert os.environ["TEST_ENV"] == "prod"
    artifact = Path(os.environ.get("BUILD_ARTIFACT", "dist/build.zip"))
    assert artifact.is_file()

    with zipfile.ZipFile(artifact) as archive:
        assert archive.testzip() is None
        manifest = json.loads(archive.read("manifest.json"))
        readme = archive.read("README.md").decode("utf-8")

    assert manifest["test_environments"] == ["staging", "prod"]
    assert manifest["version"].count(".") == 2
    assert "<!-- ACTIVITY:START -->" in readme
    assert "<!-- ACTIVITY:END -->" in readme

