from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "render_profile", ROOT / "scripts" / "render_profile.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ProfileRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((ROOT / "data" / "profile.json").read_text())
        cls.trace = MODULE.fallback_trace(cls.config)

    def _parse(self, value: str) -> None:
        ElementTree.fromstring(value)

    def test_all_authored_copies_are_valid_svg(self) -> None:
        variants = [
            MODULE.render_desktop("light", self.trace, self.config),
            MODULE.render_desktop("dark", self.trace, self.config),
            MODULE.render_mobile("light", self.trace, self.config),
            MODULE.render_mobile("dark", self.trace, self.config),
        ]
        for value in variants:
            with self.subTest(length=len(value)):
                self._parse(value)
                self.assertLess(len(value.encode()), 100_000)

    def test_night_copy_is_not_a_recolor(self) -> None:
        light = MODULE.render_desktop("light", self.trace, self.config)
        dark = MODULE.render_desktop("dark", self.trace, self.config)
        self.assertIn("That is the boring line.", light)
        self.assertIn("It lasted about ten minutes.", dark)
        self.assertNotEqual(light, dark)

    def test_mobile_is_an_authored_layout(self) -> None:
        desktop = MODULE.render_desktop("light", self.trace, self.config)
        mobile = MODULE.render_mobile("light", self.trace, self.config)
        self.assertIn('viewBox="0 0 1200 3820"', desktop)
        self.assertIn('viewBox="0 0 720 5860"', mobile)

    def test_previous_ai_shaped_vocabulary_is_gone(self) -> None:
        combined = "\n".join(
            [
                MODULE.render_desktop("light", self.trace, self.config),
                MODULE.render_desktop("dark", self.trace, self.config),
            ]
        ).lower()
        for phrase in (
            "current orbit",
            "latest transmission",
            "question engine",
            "the operating system",
            "observatory",
        ):
            self.assertNotIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
