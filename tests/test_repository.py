import re
import unittest
from pathlib import Path


class RepositoryTests(unittest.TestCase):
    def test_readme_contract(self):
        headings = re.findall(r"^## (.+)$", Path("README.md").read_text(), flags=re.MULTILINE)
        self.assertEqual(
            headings,
            [
                "Problem",
                "Scope",
                "Quick start",
                "Usage",
                "Architecture",
                "Reproduction",
                "Results",
                "Testing",
                "Limitations",
                "Contributing",
                "License",
            ],
        )

    def test_text_policy(self):
        roots = ["grounding", "tests", "docs", "data", "config", "results"]
        paths = [Path("README.md"), Path("CONTRIBUTING.md"), Path("SECURITY.md")]
        for root in roots:
            paths.extend(
                p
                for p in Path(root).rglob("*")
                if p.suffix in {".py", ".md", ".json", ".txt", ".jsonl"}
            )
        for path in paths:
            with self.subTest(path=path):
                self.assertNotIn(chr(0x2014), path.read_text(encoding="utf-8"))
