"""Command-line entry point used by the GitHub Actions build job."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())

