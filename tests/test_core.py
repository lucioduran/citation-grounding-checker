import copy
import json
import tempfile
import unittest
from pathlib import Path

from grounding.core import (
    deterministic,
    load_corpus,
    parse_flan,
    parse_nli,
    passage_url,
    score,
    summaries,
)

ROOT = Path(__file__).resolve().parents[1]


class CoreTests(unittest.TestCase):
    def test_corpus(self):
        cases = load_corpus(ROOT / "data/corpus.json", ROOT)
        self.assertEqual(len(cases), 48)
        for split, count in [("dev", 12), ("eval", 36)]:
            self.assertEqual(sum(c["split"] == split for c in cases), count)
        self.assertEqual({c["label_origin"] for c in cases}, {"synthetic_reference"})

    def test_invalid_corpus(self):
        good = json.loads((ROOT / "data/corpus.json").read_text())
        mutations = [
            lambda c: c[0].update(extra=1),
            lambda c: c[0].update(id=c[1]["id"]),
            lambda c: c[0].update(claim=""),
            lambda c: c[0].update(label="true"),
            lambda c: c[0].update(split="test"),
            lambda c: c[0].update(start=True),
            lambda c: c[0].update(start=-1),
            lambda c: c[0].update(end=999),
            lambda c: c[0].update(quote="wrong"),
            lambda c: c[0].update(source="../secret"),
            lambda c: c[0].update(label_origin="human"),
            lambda c: c[0].update(split="eval"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.json"
            for mutation in mutations:
                cases = copy.deepcopy(good)
                mutation(cases)
                path.write_text(json.dumps(cases))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    load_corpus(path, ROOT)
            for value in [[], {}, [None]]:
                path.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    load_corpus(path, ROOT)

    def test_rules(self):
        for passage, claim, expected in [
            ("A is red. B is blue.", "B is blue.", "supported"),
            ("A is red.", "A is not red.", "contradicted"),
            ("A is not red.", "A is red.", "contradicted"),
            ("Boats are blue.", "Boats are not blue.", "contradicted"),
            ("A is red.", "A is", "abstain"),
            ("A is red.", "B is blue.", "abstain"),
            ("A holds 20 liters.", "A holds 30 liters.", "abstain"),
        ]:
            self.assertEqual(deterministic(passage, claim)["prediction"], expected)

    def test_output_parsers(self):
        self.assertEqual(parse_flan(" Supported "), "supported")
        self.assertEqual(parse_flan("supported because"), "abstain")
        self.assertEqual(parse_nli([0.7, 0.2, 0.1]), "contradicted")
        self.assertEqual(parse_nli([0.1, 0.8, 0.1]), "supported")
        self.assertEqual(parse_nli([0.1, 0.2, 0.7]), "insufficient")
        self.assertEqual(parse_nli([0.4, 0.3, 0.3]), "abstain")
        for value in [[], [1, 1, 1], [float("nan"), 0, 1], [-1, 1, 1]]:
            with self.assertRaises(ValueError):
                parse_nli(value)

    def test_hand_calculated_metrics(self):
        rows = [
            dict(label=a, prediction=b, method="test", category="numbers")
            for a, b in [
                ("supported", "supported"),
                ("contradicted", "supported"),
                ("insufficient", "insufficient"),
                ("supported", "abstain"),
            ]
        ]
        result = score(rows)
        self.assertEqual(
            result["precision"], {"supported": 0.5, "contradicted": None, "insufficient": 1}
        )
        self.assertEqual(result["recall"]["supported"], 0.5)
        self.assertEqual(result["coverage"], 0.75)
        self.assertEqual(result["accuracy"], 0.5)
        self.assertAlmostEqual(result["selective_accuracy"], 2 / 3)
        self.assertEqual(summaries(rows)["test"]["categories"]["numbers"], result)
        self.assertIsNone(
            score([dict(label="supported", prediction="abstain")])["selective_accuracy"]
        )
        with self.assertRaises(ValueError):
            score([])

    def test_passage_links(self):
        case = load_corpus(ROOT / "data/corpus.json", ROOT)[0]
        self.assertTrue(passage_url(case, "a" * 40, ROOT).endswith("/data/passages/p01.txt#L1-L1"))
        with self.assertRaises(ValueError):
            passage_url(case, "main", ROOT)
