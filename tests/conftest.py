"""Test configuration."""

import sys
from pathlib import Path

import pytest

# Ensure the project root is importable when running tests via uv/pytest.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def wpt_test_data_dir() -> Path:
    data_dir = ROOT / "tests" / "conformance" / "data"
    meta_file = data_dir / "wpt_url_test_data_meta.json"
    if not meta_file.exists():
        pytest.skip(
            "WPT URL test data is missing. Fetch it with: "
            "python util/wpt_url_test_data.py download --dest_dir tests/conformance/data --commit <WPT_URL_COMMIT>"
        )
    return data_dir
