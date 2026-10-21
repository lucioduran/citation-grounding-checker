import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from grounding.__main__ import main
from grounding.experiment import run, verify
from grounding.models import PROMPT


class FakeJudge:
    def __init__(self, method, cache):
        self.method = method
        self.files = {"model.safetensors": "a" * 64}

    def predict(self, passage, claim):
        if self.method == "flan":
            return dict(
                prediction="supported",
                raw="supported",
                prompt=PROMPT.format(passage=passage, claim=claim),
                input_tokens=10,
            )
        return dict(prediction="insufficient", probabilities=[0.1, 0.1, 0.8], input_tokens=10)


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "run"
        with (
            patch("grounding.experiment.Judge", FakeJudge),
            patch("grounding.experiment.revision", return_value="a" * 40),
            patch("grounding.experiment.subprocess.check_output", return_value=""),
            patch("grounding.experiment.importlib.metadata.version", return_value="test"),
        ):
            run("dev", self.path, Path("unused"))
        self.report = self.path / "report.json"

    def test_record_and_verify(self):
        self.assertEqual(verify(self.report)["predictions"], 36)
        self.assertEqual(len((self.path / "trace.jsonl").read_text().splitlines()), 36)
        with self.assertRaises(FileExistsError):
            run("dev", self.path, Path("unused"))

    def test_tampering(self):
        original = json.loads(self.report.read_text())
        mutations = [
            lambda r: r.update(schema_version=2),
            lambda r: r.update(hashes={}),
            lambda r: r["rows"].pop(),
            lambda r: r["rows"].append(r["rows"][0]),
            lambda r: r["rows"][0].update(claim="changed"),
            lambda r: r["rows"][0].update(passage_url="https://example.org"),
            lambda r: r["rows"][0]["result"].update(reason="changed"),
            lambda r: r["rows"][12]["result"].update(prompt="changed"),
            lambda r: r["rows"][12].update(prediction="contradicted"),
            lambda r: r["rows"][12]["result"].update(input_tokens=999),
            lambda r: r.update(summary={}),
            lambda r: r.update(models={}),
            lambda r: r["models"]["nli"].update(spec={}),
        ]
        for mutation in mutations:
            report = copy.deepcopy(original)
            mutation(report)
            self.report.write_text(json.dumps(report))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify(self.report)

    def test_cli(self):
        for args, status in [
            (["validate"], 0),
            (["check", "--passage", "A.", "--claim", "A."], 0),
            (["verify", "--report", str(self.report)], 0),
            (["verify", "--report", "missing.json"], 2),
        ]:
            with contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(main(args), status)
            self.assertIsInstance(json.loads(stream.getvalue()), dict)

    def test_dirty_tree(self):
        with patch("grounding.experiment.subprocess.check_output", return_value=" M file"):
            with self.assertRaisesRegex(ValueError, "Commit"):
                run("eval", self.path, Path("unused"))
