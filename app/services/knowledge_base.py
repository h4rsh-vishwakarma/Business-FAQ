from __future__ import annotations

import json
from pathlib import Path


def load_faqs(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data["faqs"]
