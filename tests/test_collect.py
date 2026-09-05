from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from maxwell_lab.collect import write_json


class WriteJsonTests(unittest.TestCase):
    def test_write_json_creates_parent_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "nested" / "inventory.json"
            write_json(output, {"b": 2, "a": 1})
            self.assertTrue(output.exists())
            self.assertEqual(
                output.read_text(encoding="utf-8"),
                '{\n  "a": 1,\n  "b": 2\n}\n',
            )


if __name__ == "__main__":
    unittest.main()
