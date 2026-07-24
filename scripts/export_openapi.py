import json
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.api.main import app

docs_dir = BASE_DIR / "docs"
docs_dir.mkdir(exist_ok=True)

with open(docs_dir / "openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)

print("[SUCCESS] OpenAPI spec exported to docs/openapi.json")