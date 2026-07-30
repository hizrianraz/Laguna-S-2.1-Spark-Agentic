import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PULL = ROOT / "scripts" / "pull_official_gguf.sh"
SERVE = ROOT / "scripts" / "serve_spark.sh"
SKU = ROOT / "scripts" / "pull_sku.sh"
MODEL_NAME = "laguna-s-2.1-Q4_K_M.gguf"


class PullPathGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path.home())
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_pull(self, destination, *args):
        env = os.environ.copy()
        env["LAGUNA_MODEL_DIR"] = str(destination)
        env["LAGUNA_ALLOWED_MODEL_ROOT"] = str(Path(str(destination).rstrip("/")).parent)
        return subprocess.run([str(PULL), *args], env=env, text=True, capture_output=True, check=False)

    def test_dotdot_filename_is_rejected_before_destination_write(self):
        destination = self.base / "models" / "laguna-s-2.1"
        destination.parent.mkdir()
        result = self.run_pull(destination, "..")
        self.assertEqual(result.returncode, 2)
        self.assertIn("accepts only", result.stderr)
        self.assertFalse(destination.exists())

    def test_symlinked_destination_is_rejected_without_external_write(self):
        outside = self.base / "outside"
        outside.mkdir()
        destination = self.base / "laguna-s-2.1"
        destination.symlink_to(outside, target_is_directory=True)
        result = self.run_pull(str(destination) + "///")
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_hardlinked_partial_is_rejected_before_curl(self):
        destination = self.base / "models" / "laguna-s-2.1"
        destination.mkdir(parents=True)
        victim = self.base / "victim"
        victim.write_text("preserve\n")
        os.link(victim, destination / f".{MODEL_NAME}.part")
        result = self.run_pull(destination)
        self.assertEqual(result.returncode, 2)
        self.assertIn("hard link", result.stderr)
        self.assertEqual(victim.read_text(), "preserve\n")

    def test_experimental_router_is_fail_closed(self):
        result = subprocess.run([str(SKU), "unsloth-ud-iq3-s"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("no audited exact-byte manifest", result.stderr)

    def test_inherited_path_cannot_shadow_integrity_tools(self):
        fake_bin = self.base / "fake-bin"
        fake_bin.mkdir()
        marker = self.base / "shadow-called"
        for name in ("dirname", "python3", "sha256sum", "stat"):
            fake = fake_bin / name
            fake.write_text(f"#!/bin/sh\nprintf '%s\\n' {name} >>'{marker}'\nexit 91\n")
            fake.chmod(0o755)
        destination = self.base / "models" / "laguna-s-2.1"
        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "LAGUNA_MODEL_DIR": str(destination),
                "LAGUNA_ALLOWED_MODEL_ROOT": str(destination.parent),
            }
        )
        result = subprocess.run([str(PULL), ".."], env=env, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())

    def test_double_slash_tmp_root_cannot_bypass_temporary_root_deny(self):
        env = os.environ.copy()
        env.update(
            {
                "LAGUNA_ALLOWED_MODEL_ROOT": "//tmp/saqs-bypass/models",
                "LAGUNA_MODEL_DIR": "//tmp/saqs-bypass/models/laguna-s-2.1///",
            }
        )
        result = subprocess.run([str(PULL)], env=env, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertTrue("temporary" in result.stderr or "symlink component" in result.stderr)

    def test_privileged_startup_ignores_bash_env(self):
        marker = self.base / "bash-env-ran"
        startup = self.base / "hostile-bash-env"
        startup.write_text(f"printf owned > {marker!s}\n")
        destination = self.base / "models" / "laguna-s-2.1"
        destination.parent.mkdir()
        env = os.environ.copy()
        env.update(
            {
                "BASH_ENV": str(startup),
                "LAGUNA_MODEL_DIR": str(destination),
                "LAGUNA_ALLOWED_MODEL_ROOT": str(destination.parent),
            }
        )
        subprocess.run([str(PULL), ".."], env=env, text=True, capture_output=True, check=False)
        self.assertFalse(marker.exists())

    def test_isolated_python_ignores_sitecustomize(self):
        marker = self.base / "sitecustomize-ran"
        hostile = self.base / "hostile-python"
        hostile.mkdir()
        (hostile / "sitecustomize.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('owned')\n")
        destination = self.base / "models" / "laguna-s-2.1"
        destination.parent.mkdir()
        env = os.environ.copy()
        env.update(
            {
                "PYTHONPATH": str(hostile),
                "PYTHONHOME": str(hostile),
                "LAGUNA_MODEL_DIR": str(destination),
                "LAGUNA_ALLOWED_MODEL_ROOT": str(destination.parent),
            }
        )
        result = subprocess.run([str(PULL), ".."], env=env, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())


class ServeGuardSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SERVE.read_text()

    def test_secret_is_unexported_before_candidate_execution(self):
        unset_at = self.source.index("unset LAGUNA_API_KEY OPENAI_API_KEY")
        version_at = self.source.index('"${SERVER_BOUND}" --version')
        self.assertLess(unset_at, version_at)

    def test_xtrace_cannot_print_bearer_secret(self):
        sentinel = "SAQS_SENTINEL_KEY_0123456789abcdef0123456789abcdef"
        env = os.environ.copy()
        env["LAGUNA_API_KEY"] = sentinel
        result = subprocess.run(
            ["/bin/bash", "-x", str(SERVE)], env=env, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 126)
        self.assertNotIn(sentinel, result.stdout)
        self.assertNotIn(sentinel, result.stderr)

    def test_bash_env_and_exported_functions_cannot_observe_secret(self):
        sentinel = "SAQS_BOOTSTRAP_SENTINEL_0123456789abcdef0123456789abcdef"
        with tempfile.TemporaryDirectory(dir=Path.home()) as tmp:
            base = Path(tmp)
            marker = base / "bash-env-ran"
            startup = base / "hostile-bash-env"
            startup.write_text(f"printf '%s' \"$LAGUNA_API_KEY\" > {marker!s}\n")
            env = os.environ.copy()
            env.update(
                {
                    "LAGUNA_API_KEY": sentinel,
                    "BASH_ENV": str(startup),
                    "BASH_FUNC_unset%%": '() { printf "FUNC=%s\\n" "$LAGUNA_API_KEY" >&2; }',
                    "BASH_FUNC_cd%%": '() { printf "CD=%s\\n" "$LAGUNA_API_KEY" >&2; }',
                    "BASH_FUNC_basename%%": '() { printf "BASE=%s\\n" "$LAGUNA_API_KEY" >&2; }',
                }
            )
            result = subprocess.run([str(SERVE)], env=env, text=True, capture_output=True, check=False)
            self.assertFalse(marker.exists())
            self.assertNotIn(sentinel, result.stdout)
            self.assertNotIn(sentinel, result.stderr)

    def test_sourcing_is_rejected(self):
        result = subprocess.run(
            ["/bin/bash", "-p", "-c", f"source {SERVE!s}"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 126)
        self.assertIn("sourcing/plain bash is unsupported", result.stderr)

    def test_xtrace_disable_is_first_body_command(self):
        lines = self.source.splitlines()
        first_body = next(line for line in lines[1:] if line.strip() and not line.startswith("#"))
        self.assertEqual(first_body, "{ builtin set +x; } 2>/dev/null")

    def test_binary_hash_gate_precedes_version_execution(self):
        hash_at = self.source.index('actual_engine_binary_sha256="$(hash_file "${SERVER_BOUND}")"')
        expected_gate_at = self.source.index('[[ "${actual_engine_binary_sha256}" == "${EXPECTED_ENGINE_BINARY_SHA256}" ]]')
        version_at = self.source.index('"${SERVER_BOUND}" --version')
        self.assertLess(hash_at, expected_gate_at)
        self.assertLess(expected_gate_at, version_at)

    def test_hash_only_pin_phase_precedes_ldd(self):
        phase_at = self.source.index('if [[ "${PRINT_RUNTIME_PINS}" == "1" ]]')
        expected_gate_at = self.source.index('[[ "${actual_engine_binary_sha256}" == "${EXPECTED_ENGINE_BINARY_SHA256}" ]]')
        ldd_at = self.source.index('/usr/bin/ldd "${SERVER_BOUND}"')
        self.assertLess(phase_at, expected_gate_at)
        self.assertLess(expected_gate_at, ldd_at)
        self.assertIn("hash-only LAGUNA_PRINT_RUNTIME_PINS=1", self.source)

    def test_fd_binding_and_dso_closure_are_gated(self):
        self.assertIn('readonly MODEL_BOUND="/proc/$$/fd/${model_fd}"', self.source)
        self.assertIn("LAGUNA_EXPECT_DSO_MANIFEST_SHA256", self.source)
        self.assertIn("env -i", self.source)
        self.assertIn("malicious_same_uid_in_place_inode_mutation", self.source)
        self.assertIn("validate_trusted_runtime_file", self.source)

    def test_target_receipt_is_bound_to_reviewed_pack_source(self):
        self.assertIn("LAGUNA_EXPECT_PACK_REVISION", self.source)
        self.assertIn("LAGUNA_EXPECT_LAUNCHER_SHA256", self.source)
        self.assertIn('actual_launcher_sha256="$(hash_file "${LAUNCHER_PATH}")"', self.source)
        launch_at = self.source.index('/usr/bin/env -i \\\n  PATH="${CLEAN_PATH}"')
        prelaunch_recheck_at = self.source.index('"Laguna launcher changed before server launch"')
        receipt_recheck_at = self.source.index('"Laguna launcher changed before receipt creation"')
        receipt_at = self.source.index('schema: "saqs.spark_launch_receipt/v3"')
        self.assertLess(prelaunch_recheck_at, launch_at)
        self.assertLess(launch_at, receipt_recheck_at)
        self.assertLess(receipt_recheck_at, receipt_at)
        self.assertIn("declared_huggingface_revision", self.source)
        self.assertIn("launcher_digest_matched_operator_pin: true", self.source)
        self.assertIn("independently_source_bound: false", self.source)
        self.assertIn("clears_freeze: false", self.source)

    def test_successful_readiness_receipt_does_not_immediately_stop_server(self):
        receipt_publish_at = self.source.index('publish_no_clobber "${receipt_temp}" "${launch_receipt}"')
        wait_at = self.source.index('wait "${server_pid}"', receipt_publish_at)
        clear_pid_at = self.source.index('server_pid=""', wait_at)
        disable_trap_at = self.source.index('trap - EXIT INT TERM HUP', wait_at)
        self.assertLess(receipt_publish_at, wait_at)
        self.assertLess(wait_at, clear_pid_at)
        self.assertLess(clear_pid_at, disable_trap_at)

    def test_documented_launcher_pin_matches_launcher_bytes(self):
        import hashlib
        import re

        digest = hashlib.sha256(SERVE.read_bytes()).hexdigest()
        config = (ROOT / "config.yaml").read_text()
        match = re.search(r"(?m)^  launcher_sha256: ([0-9a-f]{64})$", config)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), digest)
        for relative in (
            "README.md",
            "SPARK.md",
            "docs/REPRODUCE.md",
            "docs/BUILD_SPARK.md",
            "results/LAST_GREEN_PIN.md",
            "INSTALL.yaml",
        ):
            self.assertIn(digest, (ROOT / relative).read_text(), relative)

    def test_sensitive_temporaries_use_private_runtime_directory(self):
        self.assertNotIn("mktemp -t", self.source)
        self.assertIn('runtime_parent="/run/user/${EUID}"', self.source)
        first_secret_write = self.source.index("printf '%s\\n' \"${API_KEY}\"")
        for label in ("API-key temporary", "curl-auth temporary", "wrong-auth temporary"):
            self.assertLess(self.source.index(label), first_secret_write)

    def test_embedded_python_is_absolute_clean_and_isolated(self):
        for relative in ("scripts/pull_official_gguf.sh", "scripts/serve_spark.sh"):
            source = (ROOT / relative).read_text()
            self.assertNotRegex(source, r"(?m)^\s*python3\s")
            self.assertIn("/usr/bin/python3 -I -S", source)

    def test_target_identity_is_exact_and_recorded(self):
        self.assertIn('[[ "${gpu_count}" == "1" ]]', self.source)
        self.assertIn('[[ "${gpu_name}" == *GB10* ]]', self.source)
        self.assertIn('== *"dgx spark"*', self.source)
        self.assertIn("mem_total_kib", self.source)

    def test_hostwide_lock_precedes_residency_and_server(self):
        lock_at = self.source.index('mkdir "${serve_lock_dir}"')
        pgrep_at = self.source.index('pgrep -x "${process_name}"')
        server_at = self.source.index('-m "${MODEL_BOUND}"')
        self.assertLess(lock_at, pgrep_at)
        self.assertLess(lock_at, server_at)
        self.assertIn('serve_lock_parent="/run/lock"', self.source)

    def test_inventory_errors_and_wrong_bearer_are_explicit_failures(self):
        self.assertIn("process_rc != 1", self.source)
        self.assertIn("ss port inventory failed", self.source)
        self.assertIn("wrong-token gate failed", self.source)
        self.assertIn("absent_and_wrong_bearer_rejected", self.source)

    def test_receipt_publication_is_no_clobber_and_outside_pack(self):
        self.assertIn("publish_no_clobber", self.source)
        self.assertIn("refusing broad, model, engine, or in-pack receipt directory", self.source)
        self.assertIn("launch_receipt_${receipt_stamp}.json", self.source)

    def test_every_receipt_jq_variable_is_declared(self):
        block = self.source[self.source.index("jq -n \\") : self.source.index(" > \"${receipt_temp}\"")]
        declared = set(re.findall(r"--(?:rawfile|arg|argjson)\s+([A-Za-z_][A-Za-z0-9_]*)", block))
        program = block[block.index("\n  {") :]
        referenced = set(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]*)", program))
        self.assertEqual(referenced - declared, set())

    def test_all_curl_calls_disable_user_config_first(self):
        for relative in (
            "scripts/pull_official_gguf.sh",
            "scripts/serve_spark.sh",
            "scripts/measure_layer_b_v3.sh",
        ):
            for line in (ROOT / relative).read_text().splitlines():
                if "curl --" in line:
                    self.assertIn("curl --disable", line, f"unsafe curl invocation in {relative}: {line}")

    def test_bearer_clients_disable_environment_proxies(self):
        for relative in (
            "eval/agent_smoke/run_smoke.py",
            "scripts/bench_server.py",
            "hermes/sample_client.py",
        ):
            source = (ROOT / relative).read_text()
            self.assertIn("ProxyHandler({})", source, relative)
            self.assertIn("NO_PROXY_OPENER.open", source, relative)


class ViewerSafetyTests(unittest.TestCase):
    def test_receipt_fields_are_never_inserted_with_inner_html(self):
        source = (ROOT / "eval" / "smoke_viewer.html").read_text()
        self.assertNotIn("innerHTML", source)
        self.assertIn("noteCell.textContent", source)
        self.assertIn("idCode.textContent", source)


if __name__ == "__main__":
    unittest.main()
