"""One-shot import rewrite after flattening backend/app -> backend/."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "backend", ROOT / "tests"]

REPLACEMENTS = [
    (r"from app\.core\.database import", "from database import"),
    (r"from app\.core\.security import", "from auth.security import"),
    (r"from app\.core\.deps import", "from auth.deps import"),
    (r"import app\.core\.database", "import database"),
    (r"from app\.main import", "from main import"),
    (r"from app import models", "import models"),
    (r"from app\.", "from "),
    (r"import app\.", "import "),
]


def main() -> None:
    updated = 0
    for base in TARGETS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts or ".venv" in path.parts:
                continue
            if "backend" in path.parts and path.parts.count("backend") > 1:
                # skip nested backend/backend junk
                continue
            text = path.read_text(encoding="utf-8")
            new = text
            for pat, repl in REPLACEMENTS:
                new = re.sub(pat, repl, new)
            if new != text:
                path.write_text(new, encoding="utf-8")
                updated += 1
                print(f"updated {path.relative_to(ROOT)}")
    print(f"files_updated={updated}")


if __name__ == "__main__":
    main()
