import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BENCH = load("laguna_bench_test", ROOT / "scripts" / "bench_server.py")
STAMP = load("laguna_stamp_test", ROOT / "scripts" / "_stamp_accel_receipts.py")


class BenchIntegrityTests(unittest.TestCase):
    def _run_bench(self, argv, out, *, provenance_complete=True):
        def fake_chat(base, key, model, messages, max_tokens):
            data = {
                "model": model,
                "choices": [
                    {"message": {"role": "assistant", "content": BENCH.CANONICAL_SENTINEL}}
                ],
                "error": None,
            }
            usage = {"prompt_tokens": 10, "completion_tokens": 1}
            return data, 0.1, usage

        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.dict(os.environ, {"OPENAI_API_KEY": "a" * 32}, clear=False),
            mock.patch.object(BENCH, "chat", side_effect=fake_chat),
            mock.patch.object(
                BENCH,
                "build_run_manifest",
                return_value={
                    "provenance_complete": provenance_complete,
                    "runner": {"sha256": "f" * 64},
                    "pack_git_error": None if provenance_complete else "Git unavailable",
                },
            ),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return_code = BENCH.main()
        return return_code, json.loads(out.read_text())

    def test_top_level_duplicate_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            BENCH.parse_json_strict('{"model":"other","model":"local-laguna"}')

    def test_context_marks_require_exact_complete_profile(self):
        self.assertEqual(BENCH.validate_marks(["2k", "8k"]), ["2k", "8k"])
        for marks in (["2k"], ["8k"], ["2k", "2k"], ["2k", "8k", "8k"]):
            with self.subTest(marks=marks):
                with self.assertRaises(ValueError):
                    BENCH.validate_marks(marks)

    def test_zero_completion_tokens_is_not_success(self):
        data = {"choices": [{"message": {"role": "assistant", "content": "OK"}}], "error": None}
        with self.assertRaises(ValueError):
            BENCH.validate_chat_result(data, {"prompt_tokens": 10, "completion_tokens": 0})

    def test_empty_content_is_not_success(self):
        data = {"choices": [{"message": {"role": "assistant", "content": ""}}], "error": None}
        with self.assertRaises(ValueError):
            BENCH.validate_chat_result(data, {"prompt_tokens": 10, "completion_tokens": 1})

    def test_positive_evidence_passes(self):
        data = {"choices": [{"message": {"role": "assistant", "content": "OK"}}], "error": None}
        self.assertEqual(
            BENCH.validate_chat_result(data, {"prompt_tokens": 10, "completion_tokens": 2}),
            ("OK", 10, 2),
        )

    def test_positive_token_garbage_does_not_pass_sentinel(self):
        data = {
            "choices": [{"message": {"role": "assistant", "content": "probably OK"}}],
            "error": None,
        }
        with self.assertRaises(ValueError):
            BENCH.validate_chat_result(data, {"prompt_tokens": 10, "completion_tokens": 2})

    def test_response_model_must_match_when_requested(self):
        data = {
            "model": "other",
            "choices": [{"message": {"role": "assistant", "content": "OK"}}],
            "error": None,
        }
        with self.assertRaises(ValueError):
            BENCH.validate_chat_result(
                data, {"prompt_tokens": 10, "completion_tokens": 2}, expected_model="local-laguna"
            )

    def test_response_role_must_be_assistant(self):
        data = {
            "model": "local-laguna",
            "choices": [{"message": {"role": "user", "content": "OK"}}],
            "error": None,
        }
        with self.assertRaises(ValueError):
            BENCH.validate_chat_result(
                data,
                {"prompt_tokens": 10, "completion_tokens": 2},
                expected_model="local-laguna",
            )

    def test_canonical_bench_profile_is_authority_eligible(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "canonical_bench.json"
            return_code, receipt = self._run_bench(
                [str(ROOT / "scripts" / "bench_server.py"), "--out", str(out)],
                out,
            )
            self.assertEqual(return_code, 0)
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["run_scope"], "authoritative_canonical_profile")
            self.assertTrue(receipt["request_profile_eligible"])
            self.assertTrue(receipt["authority_eligible"])
            self.assertTrue(receipt["suite_authority_eligible"])
            self.assertTrue(receipt["suite_green"])
            self.assertTrue(receipt["bench_green"])
            self.assertFalse(receipt["release_green"])
            self.assertFalse(receipt["gate_clearance"])
            self.assertNotIn("a" * 32, out.read_text())

    def test_noncanonical_bench_profiles_are_diagnostic_only(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        profiles = (
            ["--model", "other-model"],
            ["--base-url", "http://192.0.2.10:8000/v1"],
            ["--ctx-mark", "8k", "--ctx-mark", "2k"],
        )
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            for index, profile_args in enumerate(profiles):
                with self.subTest(profile_args=profile_args):
                    out = Path(tmp) / f"diagnostic_{index}.json"
                    return_code, receipt = self._run_bench(
                        [
                            str(ROOT / "scripts" / "bench_server.py"),
                            "--out", str(out),
                            *profile_args,
                        ],
                        out,
                    )
                    self.assertEqual(return_code, BENCH.NON_AUTHORITATIVE_EXIT)
                    self.assertEqual(receipt["status"], "DIAGNOSTIC_PASS")
                    self.assertEqual(receipt["run_scope"], "diagnostic_non_authoritative")
                    self.assertFalse(receipt["request_profile_eligible"])
                    self.assertFalse(receipt["authority_eligible"])
                    self.assertFalse(receipt["suite_green"])
                    self.assertFalse(receipt["release_green"])
                    self.assertFalse(receipt["gate_clearance"])

    def test_bench_manifest_binds_runner_and_git_identity(self):
        manifest = BENCH.build_run_manifest(
            base_url=BENCH.CANONICAL_BASE_URL,
            model=BENCH.CANONICAL_MODEL,
            marks=list(BENCH.CANONICAL_MARKS),
            out_path="results/future.json",
        )
        self.assertEqual(Path(manifest["runner"]["path"]), Path(BENCH.__file__).resolve())
        self.assertRegex(manifest["runner"]["sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(manifest["pack_git_head"], r"^[0-9a-f]{40}$")
        self.assertEqual(manifest["provenance_complete"], manifest["pack_git_clean"])

    def test_bench_git_absence_writes_diagnostic_receipt(self):
        with mock.patch.object(
            BENCH.subprocess,
            "check_output",
            side_effect=FileNotFoundError("git unavailable"),
        ):
            manifest = BENCH.build_run_manifest(
                base_url=BENCH.CANONICAL_BASE_URL,
                model=BENCH.CANONICAL_MODEL,
                marks=list(BENCH.CANONICAL_MARKS),
                out_path="results/future.json",
            )
        self.assertFalse(manifest["provenance_complete"])
        self.assertFalse(manifest["pack_git_clean"])
        self.assertIsNone(manifest["pack_git_head"])
        self.assertIn("Git provenance unavailable", manifest["pack_git_error"])

        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "no_git_bench.json"
            return_code, receipt = self._run_bench(
                [str(ROOT / "scripts" / "bench_server.py"), "--out", str(out)],
                out,
                provenance_complete=False,
            )
        self.assertEqual(return_code, 3)
        self.assertEqual(receipt["status"], "DIAGNOSTIC_PASS")
        self.assertEqual(receipt["run_scope"], "diagnostic_non_authoritative")
        self.assertTrue(receipt["request_profile_eligible"])
        self.assertFalse(receipt["contract"]["eligible"])
        self.assertFalse(receipt["authority_eligible"])
        self.assertFalse(receipt["suite_green"])

    def test_bench_rejects_bearer_on_command_line(self):
        with (
            mock.patch.object(
                sys,
                "argv",
                [str(ROOT / "scripts" / "bench_server.py"), "--api-key", "a" * 32],
            ),
            mock.patch.dict(os.environ, {"OPENAI_API_KEY": "b" * 32}, clear=False),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as raised,
        ):
            BENCH.main()
        self.assertEqual(raised.exception.code, 2)


class StampIntegrityTests(unittest.TestCase):
    def test_empty_receipt_never_falls_back_to_green(self):
        with self.assertRaises(ValueError):
            STAMP.summary_from({}, "empty")

    def test_zero_of_zero_is_invalid(self):
        with self.assertRaises(ValueError):
            STAMP.summary_from({"passed": 0, "n": 0, "elapsed_s": 0.0}, "zero")

    def test_row_count_must_match_claim(self):
        receipt = {
            "passed": 2,
            "n": 2,
            "elapsed_s": 1.0,
            "results": [{"id": "a", "pass": True}, {"id": "b", "pass": False}],
        }
        with self.assertRaises(ValueError):
            STAMP.summary_from(receipt, "mismatch")

    def test_valid_full_receipt_is_exact(self):
        receipt = {
            "passed": 2,
            "n": 2,
            "elapsed_s": 1.0,
            "results": [{"id": "a", "pass": True}, {"id": "b", "pass": True}],
        }
        self.assertEqual(STAMP.summary_from(receipt, "valid"), ("2/2", 1.0))

    def test_header_only_receipt_is_never_evidence(self):
        with self.assertRaises(ValueError):
            STAMP.summary_from({"passed": 2, "n": 2, "elapsed_s": 1.0}, "header-only")

    def test_bench_requires_positive_usage_and_content(self):
        with self.assertRaises(ValueError):
            STAMP.validate_bench({"rows": [{"prompt_tokens": 1, "completion_tokens": 0, "content": "OK"}]})

    def test_bench_requires_exact_unique_2k_and_8k_rows(self):
        duplicate = {
            "rows": [
                {"mark": "2k", "prompt_tokens": 1, "completion_tokens": 1, "content": "OK"},
                {"mark": "2k", "prompt_tokens": 1, "completion_tokens": 1, "content": "OK"},
            ]
        }
        with self.assertRaises(ValueError):
            STAMP.validate_bench(duplicate)


class ReleaseStateTests(unittest.TestCase):
    def test_static_source_audit_does_not_claim_runtime_or_launch_clearance(self):
        launcher_sha256 = hashlib.sha256(
            (ROOT / "scripts" / "serve_spark.sh").read_bytes()
        ).hexdigest()
        for relative in ("results/launch_lock.json", "results/RELEASE_MANIFEST.json"):
            with self.subTest(relative=relative):
                payload = json.loads((ROOT / relative).read_text())
                current = payload.get("current_source_gate") or payload.get("current_source_evidence")
                self.assertTrue(payload["audited_source_path_gates_complete"])
                self.assertTrue(current["audited_source_path_gates_complete"])
                self.assertFalse(payload["path_safety_proven"])
                self.assertFalse(current["path_safety_proven"])
                self.assertFalse(payload["verified_runnable_day0"])
                self.assertFalse(payload["launch_clearance"])
                self.assertEqual(current["launcher_sha256"], launcher_sha256)
                self.assertEqual(current["target_receipt_schema"], "saqs.spark_launch_receipt/v3")
                self.assertTrue(current["independent_source_match_required"])
                self.assertFalse(current["independent_source_match_complete"])
                self.assertFalse(current["target_receipt_self_clears_freeze"])

    def test_launch_checklist_leaves_target_and_source_match_open(self):
        launch = (ROOT / "LAUNCH_AUG3.md").read_text()
        self.assertIn("[x] Complete and independently audit the current static source path gates.", launch)
        self.assertIn("[x] Confirm the canonical standard and release metadata", launch)
        self.assertIn("[ ] Attest target-host quiescence", launch)
        self.assertIn("[ ] Produce `results/launch_receipt_aug3.json`", launch)
        self.assertIn("[ ] Independently resolve that exact Hub revision", launch)


if __name__ == "__main__":
    unittest.main()
