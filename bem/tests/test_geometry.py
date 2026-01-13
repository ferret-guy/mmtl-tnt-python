import sys
import unittest
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
MODULE_DIR = CURRENT_DIR.parent / "python"

sys.path.insert(0, str(MODULE_DIR))

from geometry import build_test1_geometry  # noqa: E402


def _normalize_xsctn_lines(lines):
    normalized = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        if stripped.lstrip().startswith("#"):
            continue
        normalized.append(stripped)
    return normalized


class GeometryTest(unittest.TestCase):
    def test_test1_geometry_matches_reference(self):
        reference_path = CURRENT_DIR / "test1.xsctn"
        geometry = build_test1_geometry()

        reference_lines = _normalize_xsctn_lines(reference_path.read_text().splitlines())
        generated_lines = _normalize_xsctn_lines(geometry.to_xsctn().splitlines())

        self.assertEqual(reference_lines, generated_lines)


if __name__ == "__main__":
    unittest.main()
