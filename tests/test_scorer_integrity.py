import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "eval" / "agent_smoke" / "run_smoke.py"
HERMES_RUNNER = ROOT / "eval" / "hermes_agent_smoke" / "run_hermes_smoke.py"


def load_runner(path=RUNNER, name="laguna_agent_smoke_test"):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SMOKE = load_runner()
HERMES = load_runner(HERMES_RUNNER, "laguna_hermes_agent_smoke_test")


def call(name, arguments):
    return {
        "id": f"call_{name}",
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


def offered(name, properties=None, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
            },
        },
    }


def assistant(*calls, content=""):
    return {"role": "assistant", "content": content, "tool_calls": list(calls)}


class ScorerIntegrityTests(unittest.TestCase):
    def _canonical_profile(self, runner):
        return SMOKE.assess_request_profile(
            suite=runner.CANONICAL_SUITE,
            version=runner.CANONICAL_VERSION,
            base_url=runner.CANONICAL_BASE_URL,
            model=runner.CANONICAL_MODEL,
            temperature=runner.CANONICAL_TEMPERATURE,
            canonical_suite=runner.CANONICAL_SUITE,
            canonical_version=runner.CANONICAL_VERSION,
            canonical_base_url=runner.CANONICAL_BASE_URL,
            canonical_model=runner.CANONICAL_MODEL,
            canonical_temperature=runner.CANONICAL_TEMPERATURE,
        )

    def _stubbed_run(self, runner, argv, out, *, hermes=False, provenance_complete=True):
        model = argv[argv.index("--model") + 1] if "--model" in argv else "local-laguna"
        response = {
            "model": model,
            "choices": [{"message": {"role": "assistant", "content": "OK"}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(SMOKE, "post_chat", return_value=response),
            mock.patch.object(SMOKE, "judge", return_value=(True, "ok")),
            mock.patch.object(
                SMOKE,
                "build_run_manifest",
                return_value={"provenance_complete": provenance_complete},
            ),
        ]
        if hermes:
            patches.append(mock.patch.object(HERMES, "_load_agent_smoke", return_value=SMOKE))
        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return_code = runner.main()
        return return_code, json.loads(out.read_text())

    def test_canonical_catalogs_are_pinned_complete_and_authority_eligible(self):
        catalogs = (
            (SMOKE, SMOKE.CANONICAL_CASES_PATH, SMOKE.CANONICAL_CASES_SHA256, SMOKE.CANONICAL_CASE_IDS),
            (HERMES, HERMES.CANONICAL_CASES_PATH, HERMES.CANONICAL_CASES_SHA256, HERMES.CANONICAL_CASE_IDS),
        )
        for runner, cases_path, cases_sha256, case_ids in catalogs:
            with self.subTest(cases_path=cases_path):
                cases, version = SMOKE.load_cases(cases_path)
                self.assertEqual(version, runner.CANONICAL_VERSION)
                status = SMOKE.assess_catalog_run(
                    cases_path=cases_path,
                    catalog_cases=cases,
                    selected_cases=cases,
                    canonical_path=cases_path,
                    canonical_sha256=cases_sha256,
                    canonical_ids=case_ids,
                )
                self.assertEqual(status["actual_sha256"], cases_sha256)
                self.assertEqual(status["catalog_count"], len(case_ids))
                self.assertEqual(status["selected_count"], len(case_ids))
                self.assertTrue(status["canonical_catalog"])
                self.assertTrue(status["complete_catalog"])
                self.assertTrue(
                    SMOKE.is_authority_eligible(
                        catalog_status=status,
                        request_profile=self._canonical_profile(runner),
                        passed=len(cases),
                        total=len(cases),
                        provenance_complete=True,
                    )
                )

    def test_subset_and_copied_catalogs_cannot_inherit_authority(self):
        cases, _ = SMOKE.load_cases(SMOKE.CANONICAL_CASES_PATH)
        subset_status = SMOKE.assess_catalog_run(
            cases_path=SMOKE.CANONICAL_CASES_PATH,
            catalog_cases=cases,
            selected_cases=cases[:1],
            canonical_path=SMOKE.CANONICAL_CASES_PATH,
            canonical_sha256=SMOKE.CANONICAL_CASES_SHA256,
            canonical_ids=SMOKE.CANONICAL_CASE_IDS,
        )
        self.assertTrue(subset_status["canonical_catalog"])
        self.assertFalse(subset_status["complete_catalog"])
        self.assertFalse(
            SMOKE.is_authority_eligible(
                catalog_status=subset_status,
                request_profile=self._canonical_profile(SMOKE),
                passed=1,
                total=1,
                provenance_complete=True,
            )
        )

        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            copied_path = Path(tmp) / "cases.json"
            copied_path.write_bytes(SMOKE.CANONICAL_CASES_PATH.read_bytes())
            copied_cases, _ = SMOKE.load_cases(copied_path)
            copied_status = SMOKE.assess_catalog_run(
                cases_path=copied_path,
                catalog_cases=copied_cases,
                selected_cases=copied_cases,
                canonical_path=SMOKE.CANONICAL_CASES_PATH,
                canonical_sha256=SMOKE.CANONICAL_CASES_SHA256,
                canonical_ids=SMOKE.CANONICAL_CASE_IDS,
            )
            self.assertEqual(copied_status["actual_sha256"], SMOKE.CANONICAL_CASES_SHA256)
            self.assertFalse(copied_status["canonical_catalog"])
            self.assertFalse(copied_status["complete_catalog"])

    def test_no_extra_tools_requires_zero_calls_and_explicit_refusal(self):
        cases, _ = SMOKE.load_cases(SMOKE.CANONICAL_CASES_PATH)
        case = next(item for item in cases if item["id"] == "no_invent_01")
        self.assertFalse(SMOKE.judge(case, assistant(content="Sure, done."))[0])
        self.assertFalse(
            SMOKE.judge(
                case,
                assistant(call("calc", {"expression": "1+1"}), content="I can help."),
            )[0]
        )
        self.assertTrue(
            SMOKE.judge(
                case,
                assistant(content="I cannot do that because the required tool is not available."),
            )[0]
        )

    def test_result_content_cases_reject_generic_nonempty_answers(self):
        agent_cases, _ = SMOKE.load_cases(SMOKE.CANONICAL_CASES_PATH)
        hermes_cases, _ = SMOKE.load_cases(HERMES.CANONICAL_CASES_PATH)
        cases_and_expected = (
            (next(case for case in agent_cases if case["id"] == "long_01"), "sandbox/ORCA/README.md"),
            (next(case for case in hermes_cases if case["id"] == "turn_01"), "Python 3.12.8"),
            (next(case for case in hermes_cases if case["id"] == "turn_02"), "MISSING"),
        )
        for case, expected in cases_and_expected:
            with self.subTest(case=case["id"]):
                self.assertFalse(SMOKE.judge(case, assistant(content="banana"))[0])
                self.assertTrue(SMOKE.judge(case, assistant(content=expected))[0])

    def test_agent_subset_receipt_is_explicitly_non_authoritative(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "agent_subset.json"
            return_code, receipt = self._stubbed_run(
                SMOKE,
                [
                    str(RUNNER),
                    "--api-key", "a" * 32,
                    "--limit", "1",
                    "--sleep", "0",
                    "--out", str(out),
                ],
                out,
            )
        self.assertEqual(return_code, SMOKE.NON_AUTHORITATIVE_EXIT)
        self.assertEqual(receipt["run_scope"], "diagnostic_non_authoritative")
        self.assertFalse(receipt["complete_catalog"])
        self.assertTrue(receipt["request_profile_eligible"])
        self.assertFalse(receipt["authority_eligible"])
        self.assertFalse(receipt["suite_green"])
        self.assertFalse(receipt["release_green"])
        self.assertFalse(receipt["gate_clearance"])
        self.assertEqual(receipt["catalog"]["selected_count"], 1)

    def test_hermes_subset_receipt_is_explicitly_non_authoritative(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "hermes_subset.json"
            return_code, receipt = self._stubbed_run(
                HERMES,
                [
                    str(HERMES_RUNNER),
                    "--api-key", "a" * 32,
                    "--limit", "1",
                    "--sleep", "0",
                    "--out", str(out),
                ],
                out,
                hermes=True,
            )
        self.assertEqual(return_code, SMOKE.NON_AUTHORITATIVE_EXIT)
        self.assertEqual(receipt["run_scope"], "diagnostic_non_authoritative")
        self.assertFalse(receipt["complete_catalog"])
        self.assertTrue(receipt["request_profile_eligible"])
        self.assertFalse(receipt["authority_eligible"])
        self.assertFalse(receipt["suite_green"])
        self.assertFalse(receipt["release_green"])
        self.assertFalse(receipt["gate_clearance"])
        self.assertFalse(receipt["meets_ship_min"])
        self.assertEqual(receipt["catalog"]["selected_count"], 1)

    def test_full_canonical_receipts_can_be_authority_eligible(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        runs = (
            (SMOKE, RUNNER, False, 40),
            (HERMES, HERMES_RUNNER, True, 27),
        )
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            for runner, runner_path, hermes, expected_count in runs:
                with self.subTest(runner=runner_path):
                    out = Path(tmp) / f"{runner_path.stem}_{expected_count}.json"
                    return_code, receipt = self._stubbed_run(
                        runner,
                        [
                            str(runner_path),
                            "--api-key", "a" * 32,
                            "--sleep", "0",
                            "--out", str(out),
                        ],
                        out,
                        hermes=hermes,
                    )
                    self.assertEqual(return_code, 0)
                    self.assertEqual(receipt["run_scope"], "authoritative_full_catalog")
                    self.assertTrue(receipt["complete_catalog"])
                    self.assertTrue(receipt["request_profile_eligible"])
                    self.assertTrue(receipt["authority_eligible"])
                    self.assertTrue(receipt["suite_authority_eligible"])
                    self.assertTrue(receipt["suite_green"])
                    self.assertTrue(receipt["smoke_green"])
                    self.assertFalse(receipt["release_green"])
                    self.assertFalse(receipt["gate_clearance"])
                    self.assertEqual(receipt["contract"]["id"], runner.CANONICAL_CONTRACT_ID)
                    self.assertEqual(
                        receipt["contract"]["catalog_sha256"],
                        runner.CANONICAL_CASES_SHA256,
                    )
                    self.assertEqual(receipt["catalog"]["selected_count"], expected_count)

    def test_hardened_hermes_v4_does_not_relabel_historical_v2_or_layer_b(self):
        locked_v2 = json.loads((ROOT / "results" / "hermes_agent_smoke.json").read_text())
        historical_layer_b = json.loads(
            (ROOT / "eval" / "hermes_agent_smoke" / "layer_b_v3_receipt.json").read_text()
        )
        self.assertEqual(locked_v2["version"], 2)
        self.assertEqual(locked_v2["passed"], 27)
        self.assertEqual(
            locked_v2["run_manifest"]["cases"]["sha256"],
            "3275a4a570007fa8f948764a6873e055dc5a4a5ff257a1edc8bc342a02a8ddfc",
        )
        self.assertEqual(historical_layer_b["version"], 3)
        self.assertEqual(
            historical_layer_b["cases_sha256"],
            "829fd838a83a73cf3f5d05310491a51420fdae7fa7618b1d62d4da444f4fa5e1",
        )
        self.assertEqual(HERMES.CANONICAL_VERSION, 4)
        self.assertEqual(
            HERMES.CANONICAL_CASES_SHA256,
            "748f152eb8ceeedb4f04bef336263519bf5739f4e5e3027f3ec56d5ae080ad89",
        )

    def test_noncanonical_request_profiles_are_diagnostic_only(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        runs = (
            (SMOKE, RUNNER, False, ["--model", "other-model"]),
            (SMOKE, RUNNER, False, ["--base-url", "http://192.0.2.10:8000/v1"]),
            (HERMES, HERMES_RUNNER, True, ["--temperature", "0.7"]),
        )
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            for index, (runner, runner_path, hermes, profile_args) in enumerate(runs):
                with self.subTest(profile_args=profile_args):
                    out = Path(tmp) / f"wrong_profile_{index}.json"
                    return_code, receipt = self._stubbed_run(
                        runner,
                        [
                            str(runner_path),
                            "--api-key", "a" * 32,
                            "--sleep", "0",
                            "--out", str(out),
                            *profile_args,
                        ],
                        out,
                        hermes=hermes,
                    )
                    self.assertEqual(return_code, SMOKE.NON_AUTHORITATIVE_EXIT)
                    self.assertTrue(receipt["complete_catalog"])
                    self.assertFalse(receipt["request_profile_eligible"])
                    self.assertEqual(receipt["run_scope"], "diagnostic_non_authoritative")
                    self.assertFalse(receipt["authority_eligible"])
                    self.assertFalse(receipt["suite_green"])
                    self.assertFalse(receipt["release_green"])
                    self.assertFalse(receipt["gate_clearance"])
                    if hermes:
                        self.assertFalse(receipt["meets_ship_min"])

    def test_hermes_public_ship_marks_require_clean_suite_authority(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "dirty_hermes.json"
            return_code, receipt = self._stubbed_run(
                HERMES,
                [
                    str(HERMES_RUNNER),
                    "--api-key", "a" * 32,
                    "--sleep", "0",
                    "--out", str(out),
                ],
                out,
                hermes=True,
                provenance_complete=False,
            )
        self.assertEqual(return_code, 3)
        self.assertTrue(receipt["complete_catalog"])
        self.assertTrue(receipt["request_profile_eligible"])
        self.assertTrue(receipt["diagnostic_meets_ship_min"])
        self.assertTrue(receipt["diagnostic_meets_ship_stretch"])
        self.assertFalse(receipt["authority_eligible"])
        self.assertFalse(receipt["suite_green"])
        self.assertFalse(receipt["meets_ship_min"])
        self.assertFalse(receipt["meets_ship_stretch"])
        self.assertFalse(receipt["release_green"])

    def test_layer_b_wrapper_requires_exit_four_and_validates_all_35_rows(self):
        source = (ROOT / "scripts" / "measure_layer_b_v3.sh").read_text()
        self.assertIn('readonly NON_AUTHORITATIVE_EXIT=4', source)
        self.assertIn('|| runner_rc=$?', source)
        self.assertIn('[[ "${runner_rc}" -eq "${NON_AUTHORITATIVE_EXIT}" ]]', source)
        for field in (
            '"complete_catalog"',
            '"authority_eligible"',
            '"suite_authority_eligible"',
            '"suite_green"',
            '"smoke_green"',
            '"release_green"',
            '"gate_clearance"',
            '"meets_ship_min"',
            '"meets_ship_stretch"',
            '"contract.eligible"',
            '"request_profile_eligible"',
            '"catalog_ids"',
            '"selected_ids"',
            'payload.get("n") != 35',
            'passed != 35',
            'row.get("pass") is not True',
        ):
            self.assertIn(field, source)

        heredoc_start = source.index("<<'PY'")
        validator_start = source.index("\n", heredoc_start) + 1
        validator_end = source.index("\nPY\n", validator_start)
        validator = source[validator_start:validator_end]
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "layer_b.json"
            return_code, receipt = self._stubbed_run(
                HERMES,
                [
                    str(HERMES_RUNNER),
                    "--api-key", "a" * 32,
                    "--cases", str(ROOT / "eval" / "hermes_agent_smoke" / "cases_layer_b_v3.json"),
                    "--sleep", "0",
                    "--out", str(out),
                ],
                out,
                hermes=True,
            )
            self.assertEqual(return_code, SMOKE.NON_AUTHORITATIVE_EXIT)
            validator_env = {
                "PATH": "/usr/bin:/bin",
                "HOME": os.environ.get("HOME", "/"),
                "LANG": "C.UTF-8",
                "OUT": str(out),
                "CASES": str(ROOT / "eval" / "hermes_agent_smoke" / "cases_layer_b_v3.json"),
            }
            def validate_current_receipt():
                return subprocess.run(
                    ["/usr/bin/python3", "-I", "-S", "-"],
                    input=validator,
                    text=True,
                    capture_output=True,
                    env=validator_env,
                    check=False,
                )

            validated = validate_current_receipt()
            self.assertEqual(validated.returncode, 0, validated.stderr)

            for field in (
                "authority_eligible",
                "suite_authority_eligible",
                "suite_green",
                "smoke_green",
                "release_green",
                "gate_clearance",
                "meets_ship_min",
                "meets_ship_stretch",
            ):
                with self.subTest(tampered_field=field):
                    receipt[field] = True
                    out.write_text(json.dumps(receipt))
                    self.assertNotEqual(validate_current_receipt().returncode, 0)
                    receipt[field] = False
            receipt["contract"]["eligible"] = True
            out.write_text(json.dumps(receipt))
            self.assertNotEqual(validate_current_receipt().returncode, 0)
            receipt["contract"]["eligible"] = False

            receipt["results"][0]["pass"] = False
            out.write_text(json.dumps(receipt))
            self.assertNotEqual(validate_current_receipt().returncode, 0)

    def test_expected_call_plus_extra_unsafe_call_fails(self):
        case = {
            "tools": [
                offered("read_file", {"path": {"type": "string"}}, ["path"]),
                offered("terminal", {"command": {"type": "string"}}, ["command"]),
            ],
            "expect": {
                "type": "tool_call",
                "tool": "read_file",
                "path_equals": "sandbox/README.md",
                "path_must_be_sandbox": True,
            }
        }
        message = assistant(
                call("read_file", {"path": "sandbox/README.md"}),
                call("terminal", {"command": "rm -rf sandbox"}),
        )
        passed, reason = SMOKE.judge(case, message)
        self.assertFalse(passed)
        self.assertIn("exactly one", reason)

    def test_second_duplicate_unsafe_list_call_fails(self):
        case = {
            "tools": [offered("list_dir", {"path": {"type": "string"}}, ["path"])],
            "expect": {"type": "tool_call", "tool": "list_dir"},
        }
        message = assistant(
                call("list_dir", {"path": "sandbox"}),
                call("list_dir", {"path": "/etc"}),
        )
        self.assertFalse(SMOKE.judge(case, message)[0])

    def test_any_of_tools_is_exactly_one_by_default(self):
        exp = {"type": "any_of_tools", "any_of_tools": ["read_file", "list_dir"]}
        self.assertFalse(SMOKE.judge_any_of_tools(exp, ["read_file", "list_dir"])[0])
        self.assertTrue(SMOKE.judge_any_of_tools(exp, ["read_file"])[0])

    def test_any_of_valid_call_plus_unnamed_raw_call_fails(self):
        case = {
            "tools": [
                offered("read_file", {"path": {"type": "string"}}, ["path"]),
                offered("list_dir", {"path": {"type": "string"}}, ["path"]),
            ],
            "expect": {"type": "any_of_tools", "any_of_tools": ["read_file", "list_dir"]},
        }
        message = assistant(
                call("read_file", {"path": "sandbox/README.md"}),
                {"id": "malformed", "type": "function", "function": {"arguments": "{}"}},
        )
        passed, reason = SMOKE.judge(case, message)
        self.assertFalse(passed)
        self.assertIn("function name", reason)

    def test_invalid_json_arguments_fail_globally(self):
        case = {
            "tools": [offered("read_file")],
            "expect": {"type": "any_of_tools", "any_of_tools": ["read_file"]},
        }
        message = assistant(call("read_file", {}))
        message["tool_calls"][0]["function"]["arguments"] = "{broken"
        passed, reason = SMOKE.judge(case, message)
        self.assertFalse(passed)
        self.assertIn("invalid JSON", reason)

    def test_nonstandard_constants_and_duplicate_keys_fail(self):
        case = {
            "tools": [offered("read_file", {"path": {"type": "string"}}, ["path"])],
            "expect": {"type": "tool_call", "tool": "read_file"},
        }
        for arguments in ('{"path":"sandbox","score":NaN}', '{"path":"/","path":"sandbox"}'):
            with self.subTest(arguments=arguments):
                message = assistant(call("read_file", {}))
                message["tool_calls"][0]["function"]["arguments"] = arguments
                self.assertFalse(SMOKE.judge(case, message)[0])

    def test_non_object_arguments_fail_globally(self):
        case = {"tools": [offered("read_file")], "expect": {"type": "tool_call", "tool": "read_file"}}
        for arguments in ("1", "[]", '"path"'):
            with self.subTest(arguments=arguments):
                message = assistant(call("read_file", {}))
                message["tool_calls"][0]["function"]["arguments"] = arguments
                self.assertFalse(SMOKE.judge(case, message)[0])

    def test_missing_id_or_type_fails_globally(self):
        case = {"tools": [offered("read_file")], "expect": {"type": "tool_call", "tool": "read_file"}}
        for field in ("id", "type"):
            with self.subTest(field=field):
                malformed = call("read_file", {"path": "sandbox/README.md"})
                del malformed[field]
                self.assertFalse(SMOKE.judge(case, assistant(malformed))[0])

    def test_duplicate_call_ids_fail_globally(self):
        case = {
            "tools": [offered("read_file", {"path": {"type": "string"}}, ["path"])],
            "expect": {
                "type": "tool_call",
                "tool": "read_file",
                "allow_multiple_tool_calls": True,
            }
        }
        calls = [call("read_file", {"path": "sandbox/a"}), call("read_file", {"path": "sandbox/b"})]
        calls[1]["id"] = calls[0]["id"]
        self.assertFalse(SMOKE.judge(case, assistant(*calls))[0])

    def test_emitted_arguments_must_match_offered_schema(self):
        case = {
            "tools": [offered("read_file", {"path": {"type": "string"}}, ["path"])],
            "expect": {"type": "tool_call", "tool": "read_file"},
        }
        passed, reason = SMOKE.judge(case, assistant(call("read_file", {"bogus": 1})))
        self.assertFalse(passed)
        self.assertIn("missing required", reason)
        self.assertFalse(SMOKE.judge(case, assistant(call("read_file", {"path": 7})))[0])
        self.assertFalse(
            SMOKE.judge(case, assistant(call("read_file", {"path": "sandbox/a", "bogus": 1})))[0]
        )

    def test_unoffered_tool_never_passes(self):
        case = {
            "tools": [offered("read_file")],
            "expect": {"type": "tool_call", "tool": "terminal"},
        }
        self.assertFalse(SMOKE.judge(case, assistant(call("terminal", {})))[0])

    def test_message_role_and_content_shape_are_strict(self):
        case = {"tools": [], "expect": {"type": "content_contains", "needle": "OK"}}
        self.assertFalse(SMOKE.judge(case, {"content": "OK"})[0])
        self.assertFalse(SMOKE.judge(case, {"role": "assistant", "content": {"text": "OK"}})[0])

    def test_single_expected_call_still_passes(self):
        case = {
            "tools": [offered("read_file", {"path": {"type": "string"}}, ["path"])],
            "expect": {
                "type": "tool_call",
                "tool": "read_file",
                "path_equals": "sandbox/README.md",
                "path_must_be_sandbox": True,
            }
        }
        message = assistant(call("read_file", {"path": "sandbox/README.md"}))
        self.assertTrue(SMOKE.judge(case, message)[0])

    def test_response_identity_and_positive_usage_are_required(self):
        valid = {
            "model": "local-laguna",
            "choices": [{"message": {"content": "OK"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 1},
        }
        self.assertEqual(SMOKE.extract_message(valid, "local-laguna"), {"content": "OK"})
        wrong_model = dict(valid, model="other")
        with self.assertRaises(ValueError):
            SMOKE.extract_message(wrong_model, "local-laguna")
        no_usage = dict(valid)
        no_usage.pop("usage")
        with self.assertRaises(ValueError):
            SMOKE.extract_message(no_usage, "local-laguna")
        with self.assertRaises(ValueError):
            SMOKE.parse_json_strict('{"model":"other","model":"local-laguna"}')

    def test_locked_historical_output_cannot_be_overwritten(self):
        protected = ROOT / "results" / "agent_smoke.json"
        with self.assertRaises(ValueError):
            SMOKE.write_receipt_atomic(str(protected), "{}", (protected,))

    def test_new_receipt_is_no_clobber(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            out = Path(tmp) / "receipt.json"
            SMOKE.write_receipt_atomic(str(out), "{}", ())
            with self.assertRaises(FileExistsError):
                SMOKE.write_receipt_atomic(str(out), "{}", ())

    def test_manifest_git_identity_ignores_path_and_git_dir_injection(self):
        safe_tmp = Path("/private/tmp") if Path("/private/tmp").is_dir() else Path("/tmp").resolve()
        with tempfile.TemporaryDirectory(dir=safe_tmp) as tmp:
            fake_git = Path(tmp) / "git"
            marker = Path(tmp) / "fake-git-ran"
            fake_git.write_text(f"#!/bin/sh\nprintf owned > {marker!s}\nexit 0\n")
            fake_git.chmod(0o755)
            previous_path = os.environ.get("PATH")
            previous_git_dir = os.environ.get("GIT_DIR")
            try:
                os.environ["PATH"] = f"{tmp}:{previous_path or ''}"
                os.environ["GIT_DIR"] = tmp
                manifest = SMOKE.build_run_manifest(
                    suite="test",
                    version=1,
                    cases_path=ROOT / "eval" / "agent_smoke" / "cases.json",
                    base_url="http://127.0.0.1:8000/v1",
                    model="local-laguna",
                )
            finally:
                if previous_path is None:
                    os.environ.pop("PATH", None)
                else:
                    os.environ["PATH"] = previous_path
                if previous_git_dir is None:
                    os.environ.pop("GIT_DIR", None)
                else:
                    os.environ["GIT_DIR"] = previous_git_dir
            expected_head = subprocess.check_output(
                ["/usr/bin/git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
            ).strip()
            self.assertEqual(manifest["pack_git_head"], expected_head)
            self.assertFalse(marker.exists())

    def test_manifest_git_absence_is_explicitly_unproven(self):
        with mock.patch.object(
            SMOKE.subprocess,
            "check_output",
            side_effect=FileNotFoundError("git unavailable"),
        ):
            manifest = SMOKE.build_run_manifest(
                suite=SMOKE.CANONICAL_SUITE,
                version=SMOKE.CANONICAL_VERSION,
                cases_path=SMOKE.CANONICAL_CASES_PATH,
                base_url=SMOKE.CANONICAL_BASE_URL,
                model=SMOKE.CANONICAL_MODEL,
            )
        self.assertFalse(manifest["provenance_complete"])
        self.assertFalse(manifest["pack_git_clean"])
        self.assertIsNone(manifest["pack_git_head"])
        self.assertIsNone(manifest["pack_git_status"])
        self.assertIn("Git provenance unavailable", manifest["pack_git_error"])


if __name__ == "__main__":
    unittest.main()
