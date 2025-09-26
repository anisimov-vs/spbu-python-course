# scripts/shared.py
from __future__ import annotations

import os
import pathlib

ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent
DOCS: pathlib.Path = ROOT / "docs"
TESTS: pathlib.Path = ROOT / "tests"


def configure_python_path() -> None:
    python_path: str | None = os.getenv("PYTHONPATH")
    if python_path is None:
        os.environ["PYTHONPATH"] = str(ROOT)
    else:
        os.environ["PYTHONPATH"] = python_path + ";" + str(ROOT)
    print("Configure python path: ", os.environ["PYTHONPATH"])
