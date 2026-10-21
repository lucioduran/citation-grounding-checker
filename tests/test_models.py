import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from grounding.models import Judge, download


class ModelTests(unittest.TestCase):
    def test_download_is_pinned(self):
        hub = MagicMock()
        with patch.dict("sys.modules", huggingface_hub=hub):
            download(Path("cache"))
        self.assertEqual(hub.snapshot_download.call_count, 2)
        for call in hub.snapshot_download.call_args_list:
            self.assertEqual(len(call.kwargs["revision"]), 40)
            self.assertFalse(call.kwargs["token"])
            self.assertIn("model.safetensors", call.kwargs["allow_patterns"])

    def test_offline_adapter_and_token_budget(self):
        torch, transformers = MagicMock(), MagicMock()
        tokenizer = transformers.AutoTokenizer.from_pretrained.return_value
        encoded = {"input_ids": MagicMock()}
        encoded["input_ids"].shape = [1, 20]
        tokenizer.return_value = encoded
        tokenizer.decode.return_value = "supported"
        flan = transformers.AutoModelForSeq2SeqLM.from_pretrained.return_value.eval.return_value
        nli = transformers.AutoModelForSequenceClassification.from_pretrained.return_value.eval.return_value
        nli.config.id2label = {0: "contradiction", 1: "entailment", 2: "neutral"}
        nli.return_value.logits.softmax.return_value.__getitem__.return_value.tolist.return_value = [
            0.1,
            0.8,
            0.1,
        ]
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict("sys.modules", torch=torch, transformers=transformers),
            patch("grounding.models.model_path", return_value=Path(directory)),
        ):
            for method in ("flan", "nli"):
                judge = Judge(method, Path(directory))
                self.assertEqual(judge.predict("Evidence.", "Claim.")["prediction"], "supported")
            for factory in (
                transformers.AutoModelForSeq2SeqLM,
                transformers.AutoModelForSequenceClassification,
            ):
                kwargs = factory.from_pretrained.call_args.kwargs
                self.assertTrue(kwargs["local_files_only"])
                self.assertTrue(kwargs["use_safetensors"])
                self.assertFalse(kwargs["trust_remote_code"])
            self.assertFalse(flan.generate.call_args.kwargs["do_sample"])
            encoded["input_ids"].shape = [1, 385]
            with self.assertRaisesRegex(ValueError, "truncation"):
                judge.predict("Long.", "Claim.")
            nli.config.id2label = {}
            with self.assertRaisesRegex(ValueError, "mapping"):
                Judge("nli", Path(directory))
            with self.assertRaisesRegex(ValueError, "Unknown"):
                Judge("other", Path(directory))
