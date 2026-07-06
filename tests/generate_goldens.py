#!/usr/bin/env python3
"""Regenerate the golden scaffold trees in tests/golden/.

Run only when a template change is intentional, then review the diff:
    python3 tests/generate_goldens.py
The pytest suite compares scripts/init_project.py output against these trees
byte for byte, so an unreviewed regeneration defeats the tests' purpose.
"""

import shutil
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR.parent / "scripts"))

from init_project import build_files  # noqa: E402

GOLDEN_DIR = TESTS_DIR / "golden"

# Case name -> build_files kwargs. Kept in one place so the tests import it and
# stay in step with what the goldens actually contain.
GOLDEN_CASES = {
    "level1": dict(departments=["engineering"], level=1, existing=False),
    "level2": dict(departments=["engineering"], level=2, existing=False),
    "level3": dict(departments=["engineering"], level=3, existing=False),
    "level4": dict(departments=["engineering"], level=4, existing=False),
    "level3-existing": dict(departments=["engineering", "design"], level=3, existing=True),
}

GOLDEN_PROJECT_NAME = "Golden Sample"
GOLDEN_TODAY = "2026-01-01"


def build_case(case_kwargs, root: Path) -> dict:
    return build_files(
        project_name=GOLDEN_PROJECT_NAME,
        output_dir=root,
        today=GOLDEN_TODAY,
        **case_kwargs,
    )


def main() -> None:
    for case, kwargs in GOLDEN_CASES.items():
        case_dir = GOLDEN_DIR / case
        if case_dir.exists():
            shutil.rmtree(case_dir)
        root = Path(".")
        for path, content in build_case(kwargs, root).items():
            target = case_dir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        print(f"regenerated {case_dir}")


if __name__ == "__main__":
    main()
