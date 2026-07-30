#!/usr/bin/python3 -I
"""Fixed agent_smoke runner for Laguna OpenAI-compatible servers.

Pass/fail only against the pinned cases.json — no free-form grading.
Fixed smoke runner
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import resource
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

CANONICAL_CASES_PATH = Path(__file__).resolve().with_name("cases.json")
CANONICAL_CASES_SHA256 = "74be7febe87fab49213f21d33c6b36a504a58a86791cc7d3961e63ce5e7abf76"
CANONICAL_SUITE = "agent_smoke"
CANONICAL_VERSION = 2
CANONICAL_BASE_URL = "http://127.0.0.1:8000/v1"
CANONICAL_MODEL = "local-laguna"
CANONICAL_TEMPERATURE = 0.0
CANONICAL_CONTRACT_ID = "agent_smoke/v2"
CANONICAL_CASE_IDS = (
    "tool_json_01", "tool_json_02", "tool_json_03", "tool_json_04",
    "tool_json_05", "tool_json_06", "tool_json_07", "tool_json_08",
    "multi_01", "multi_02", "multi_03", "multi_04", "multi_05", "multi_06", "multi_07", "multi_08",
    "repair_01", "repair_02", "repair_03", "repair_04", "repair_05", "repair_06",
    "no_invent_01", "no_invent_02", "no_invent_03", "no_invent_04", "no_invent_05", "no_invent_06",
    "code_01", "code_02", "code_03", "code_04", "code_05", "code_06",
    "long_01", "long_02", "long_03", "long_04", "long_05", "long_06",
)
NON_AUTHORITATIVE_EXIT = 4

def load_cases(path: Path):
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("cases file must contain a cases array")
    cases = data["cases"]
    if not cases:
        raise ValueError("cases file must not be empty")
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(cases) or any(not case_id for case_id in ids):
        raise ValueError("every case must be an object with a non-empty id")
    if len(set(ids)) != len(ids):
        raise ValueError("case ids must be unique")
    declared_n = data.get("n")
    if declared_n is not None and declared_n != len(cases):
        raise ValueError(f"declared n={declared_n} does not match {len(cases)} cases")
    return cases, data.get("version", 1)


def assess_catalog_run(
    *,
    cases_path: str | Path,
    catalog_cases: list[dict],
    selected_cases: list[dict],
    canonical_path: str | Path,
    canonical_sha256: str,
    canonical_ids: tuple[str, ...],
) -> dict:
    """Classify a run without allowing a subset or copied catalog to inherit authority."""
    actual_path = Path(os.path.abspath(os.path.expanduser(os.fspath(cases_path))))
    expected_path = Path(os.path.abspath(os.path.expanduser(os.fspath(canonical_path))))
    actual_sha256 = hashlib.sha256(actual_path.read_bytes()).hexdigest()
    catalog_ids = tuple(case["id"] for case in catalog_cases)
    selected_ids = tuple(case["id"] for case in selected_cases)
    path_is_canonical = actual_path == expected_path and not actual_path.is_symlink()
    canonical_catalog = bool(
        path_is_canonical
        and actual_sha256 == canonical_sha256
        and len(catalog_cases) == len(canonical_ids)
        and catalog_ids == canonical_ids
    )
    complete_catalog = bool(canonical_catalog and selected_ids == canonical_ids)
    return {
        "canonical_path": str(expected_path),
        "actual_path": str(actual_path),
        "canonical_sha256": canonical_sha256,
        "actual_sha256": actual_sha256,
        "canonical_count": len(canonical_ids),
        "catalog_count": len(catalog_cases),
        "selected_count": len(selected_cases),
        "catalog_ids": list(catalog_ids),
        "selected_ids": list(selected_ids),
        "canonical_catalog": canonical_catalog,
        "complete_catalog": complete_catalog,
    }


def assess_request_profile(
    *,
    suite: str,
    version: int,
    base_url: str,
    model: str,
    temperature: float,
    canonical_suite: str,
    canonical_version: int,
    canonical_base_url: str,
    canonical_model: str,
    canonical_temperature: float,
) -> dict:
    actual = {
        "suite": suite,
        "version": version,
        "base_url": base_url,
        "model": model,
        "temperature": temperature,
    }
    expected = {
        "suite": canonical_suite,
        "version": canonical_version,
        "base_url": canonical_base_url,
        "model": canonical_model,
        "temperature": canonical_temperature,
    }
    return {
        "actual": actual,
        "expected": expected,
        "canonical_request_profile": actual == expected,
    }


def is_authority_eligible(
    *,
    catalog_status: dict,
    request_profile: dict,
    passed: int,
    total: int,
    provenance_complete: bool,
) -> bool:
    return bool(
        catalog_status.get("complete_catalog")
        and request_profile.get("canonical_request_profile")
        and provenance_complete
        and total > 0
        and passed == total
    )


def build_run_manifest(
    *,
    suite: str,
    version,
    cases_path: Path,
    base_url: str,
    model: str,
    temperature: float = 0.0,
    out_path: str | None = None,
    runner_path: str | Path | None = None,
) -> dict:
    """Provenance block attached to every smoke receipt.

    runner_path: optional override for wrappers (e.g. hermes_agent_smoke) so the
    stamped runner is the entrypoint script, not this helper module.
    """
    cases_path = Path(cases_path)
    runner_file = Path(runner_path).resolve() if runner_path else Path(__file__).resolve()
    judge_file = Path(__file__).resolve()
    cases_sha = hashlib.sha256(cases_path.read_bytes()).hexdigest()
    runner_sha = hashlib.sha256(runner_file.read_bytes()).hexdigest()
    judge_sha = hashlib.sha256(judge_file.read_bytes()).hexdigest()
    # Prefer pack root from helper location (…/eval/agent_smoke → pack root parents[2]).
    root = judge_file.parents[2]
    git_env = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }
    git_head = None
    git_status = None
    git_error = None
    try:
        git_head = (
            subprocess.check_output(
                ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                timeout=5,
                env=git_env,
            )
            .decode()
            .strip()
        )
        git_status = (
            subprocess.check_output(
                [
                    "/usr/bin/git",
                    "-C",
                    str(root),
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ],
                stderr=subprocess.DEVNULL,
                timeout=10,
                env=git_env,
            )
            .decode()
            .splitlines()
        )
    except (OSError, subprocess.SubprocessError) as exc:
        git_head = None
        git_status = None
        git_error = f"{type(exc).__name__}: Git provenance unavailable"
    return {
        "schema": "laguna.run_manifest/v1",
        "suite": suite,
        "suite_version": version,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "runner": {
            "path": str(runner_file),
            "sha256": runner_sha,
        },
        "judge": {
            "path": str(judge_file),
            "sha256": judge_sha,
        },
        "cases": {
            "path": str(cases_path.resolve()) if cases_path.exists() else str(cases_path),
            "sha256": cases_sha,
        },
        "request": {
            "base_url": base_url,
            "model": model,
            "temperature": temperature,
        },
        "pack_git_head": git_head,
        "pack_git_clean": git_status == [],
        "pack_git_status": git_status,
        "pack_git_error": git_error,
        "provenance_complete": bool(
            isinstance(git_head, str)
            and re.fullmatch(r"[0-9a-f]{40}", git_head)
            and re.fullmatch(r"[0-9a-f]{64}", cases_sha)
            and re.fullmatch(r"[0-9a-f]{64}", runner_sha)
            and re.fullmatch(r"[0-9a-f]{64}", judge_sha)
            and git_status == []
        ),
        "out": out_path,
        "env_note": {
            "LAGUNA_MODEL": os.environ.get("LAGUNA_MODEL"),
            "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL"),
        },
        "protocol": "one-response protocol; tools validated not executed",
    }


def post_chat(base_url: str, api_key: str, model: str, messages, tools, temperature=0.0, max_tokens=512, timeout=180):
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "laguna-agent-smoke/1.0",
        },
        method="POST",
    )
    with NO_PROXY_OPENER.open(req, timeout=timeout) as resp:
        return parse_json_strict(resp.read().decode())


def extract_message(resp, expected_model: str | None = None):
    """Return one attributable response message or reject the receipt."""
    if not isinstance(resp, dict) or resp.get("error") is not None:
        raise ValueError("response must be an error-free JSON object")
    if expected_model is not None and resp.get("model") != expected_model:
        raise ValueError(f"response model must equal {expected_model!r}")
    choices = resp.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError("response must contain exactly one choice")
    choice = choices[0]
    message = choice.get("message") if isinstance(choice, dict) else None
    if not isinstance(message, dict):
        raise ValueError("response choice must contain one message object")
    usage = resp.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("response must contain usage evidence")
    for key in ("prompt_tokens", "completion_tokens"):
        value = usage.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"usage.{key} must be a positive integer")
    return message


def tool_names(msg):
    names = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function") or {}
        n = fn.get("name")
        if n:
            names.append(n)
    # some servers put calls in content as JSON — do not count as valid tools
    return names


def _reject_json_constant(value):
    raise ValueError(f"non-standard JSON constant: {value}")


def _unique_json_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON object key: {key}")
        obj[key] = value
    return obj


def parse_json_strict(raw: str):
    return json.loads(
        raw,
        parse_constant=_reject_json_constant,
        object_pairs_hook=_unique_json_object,
    )


def parse_args_map(msg):
    out = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function") or {}
        raw = fn.get("arguments") or "{}"
        try:
            args = parse_json_strict(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, ValueError):
            args = {"__raw__": raw, "__invalid_json__": True}
        out.append({"name": fn.get("name"), "arguments": args})
    return out


def validate_tool_calls(msg) -> tuple[bool, str, list[dict], list[str]]:
    """Validate every raw OpenAI tool call before expectation-specific grading."""
    raw_calls = msg.get("tool_calls")
    if raw_calls is None:
        return True, "ok", [], []
    if not isinstance(raw_calls, list):
        return False, "tool_calls must be an array", [], []

    parsed: list[dict] = []
    names: list[str] = []
    call_ids: list[str] = []
    for index, raw_call in enumerate(raw_calls):
        if not isinstance(raw_call, dict):
            return False, f"tool call {index} must be an object", [], []
        call_id = raw_call.get("id")
        if not isinstance(call_id, str) or not call_id.strip():
            return False, f"tool call {index} lacks a non-empty string id", [], []
        if raw_call.get("type") != "function":
            return False, f"tool call {index} type must equal 'function'", [], []
        function = raw_call.get("function")
        if not isinstance(function, dict):
            return False, f"tool call {index}.function must be an object", [], []
        name = function.get("name")
        if not isinstance(name, str) or not name.strip():
            return False, f"tool call {index} lacks a non-empty function name", [], []
        raw_arguments = function.get("arguments")
        if not isinstance(raw_arguments, str) or not raw_arguments.strip():
            return False, f"tool call {index} arguments must be a non-empty JSON string", [], []
        try:
            arguments = parse_json_strict(raw_arguments)
        except (json.JSONDecodeError, ValueError):
            return False, f"tool call {index} arguments are invalid JSON", [], []
        if not isinstance(arguments, dict):
            return False, f"tool call {index} arguments must decode to a JSON object", [], []
        call_ids.append(call_id)
        names.append(name)
        parsed.append({"name": name, "arguments": arguments})

    if len(set(call_ids)) != len(call_ids):
        return False, "tool call ids must be unique", [], []
    return True, "ok", parsed, names


def _schema_type_matches(value, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_json_schema(value, schema, path: str = "$") -> tuple[bool, str]:
    """Validate the JSON-Schema subset used by the pinned smoke catalogs."""
    if not isinstance(schema, dict):
        return False, f"{path} schema must be an object"
    expected = schema.get("type")
    if expected is not None:
        expected_types = expected if isinstance(expected, list) else [expected]
        if not expected_types or any(not isinstance(item, str) for item in expected_types):
            return False, f"{path} schema has invalid type declaration"
        if not any(_schema_type_matches(value, item) for item in expected_types):
            return False, f"{path} must have type {'|'.join(expected_types)}"
    if "enum" in schema and value not in schema["enum"]:
        return False, f"{path} is not an allowed enum value"
    if "const" in schema and value != schema["const"]:
        return False, f"{path} does not equal the required constant"
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list) or any(
            not isinstance(item, str) for item in required
        ):
            return False, f"{path} schema has invalid object constraints"
        missing = [key for key in required if key not in value]
        if missing:
            return False, f"{path} is missing required key(s): {','.join(missing)}"
        # The smoke catalog is intentionally closed-world even when a legacy
        # schema omitted JSON Schema's permissive additionalProperties default.
        if schema.get("additionalProperties", False) is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                return False, f"{path} has unexpected key(s): {','.join(extra)}"
        for key, child in value.items():
            if key in properties:
                ok, reason = validate_json_schema(child, properties[key], f"{path}.{key}")
                if not ok:
                    return False, reason
    if isinstance(value, list) and "items" in schema:
        for index, child in enumerate(value):
            ok, reason = validate_json_schema(child, schema["items"], f"{path}[{index}]")
            if not ok:
                return False, reason
    return True, "ok"


def validate_calls_against_case(case, calls) -> tuple[bool, str]:
    offered = case.get("tools")
    if not isinstance(offered, list):
        return False, "case tools must be an array"
    catalog = {}
    for index, tool in enumerate(offered):
        function = tool.get("function") if isinstance(tool, dict) and tool.get("type") == "function" else None
        name = function.get("name") if isinstance(function, dict) else None
        parameters = function.get("parameters") if isinstance(function, dict) else None
        if not isinstance(name, str) or not name or not isinstance(parameters, dict):
            return False, f"offered tool {index} has an invalid function schema"
        if name in catalog:
            return False, f"offered tool name {name!r} is duplicated"
        catalog[name] = parameters
    for call in calls:
        name = call["name"]
        if name not in catalog:
            return False, f"tool {name!r} was not offered by this case"
        ok, reason = validate_json_schema(call["arguments"], catalog[name])
        if not ok:
            return False, f"tool {name} arguments violate offered schema: {reason}"
    return True, "ok"


def _is_valid_json_args(raw) -> bool:
    if raw is None:
        return True
    if not isinstance(raw, str):
        return True
    try:
        parse_json_strict(raw if raw.strip() else "{}")
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def sanitize_messages_for_server(messages):
    """Coerce historical assistant tool-call arguments to valid JSON.

    llama-server and similar engines re-parse prior tool_call.arguments and
    HTTP 500 on invalid JSON before the model runs. A Hermes-class client
    must not forward raw broken args; keep the tool error turn, replace the
    broken arguments string with a valid JSON envelope that preserves the raw
    text for context. This keeps repair_04 a model test, not an engine crash.
    """
    out = []
    for m in messages:
        mm = dict(m)
        tcs = mm.get("tool_calls")
        if tcs:
            new_tcs = []
            for tc in tcs:
                tc2 = dict(tc)
                fn = dict(tc2.get("function") or {})
                raw = fn.get("arguments")
                if not _is_valid_json_args(raw):
                    fn["arguments"] = json.dumps(
                        {
                            "_invalid_json_arguments": True,
                            "_raw": raw if isinstance(raw, str) else repr(raw),
                        },
                        ensure_ascii=False,
                    )
                tc2["function"] = fn
                new_tcs.append(tc2)
            mm["tool_calls"] = new_tcs
        out.append(mm)
    return out



def _norm_path(p) -> str:
    """Normalize path strings for equality / sandbox checks (smoke labels only)."""
    if p is None:
        return ""
    if not isinstance(p, str):
        p = str(p)
    s = p.strip().replace("\\", "/")
    # drop surrounding quotes models sometimes emit
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1]
    while "//" in s:
        s = s.replace("//", "/")
    # strip leading ./ segments
    while s.startswith("./"):
        s = s[2:]
    # collapse trailing slash except root
    if len(s) > 1 and s.endswith("/"):
        s = s.rstrip("/")
    return s


def _path_under_sandbox(p) -> bool:
    """True iff path is a relative sandbox/... path (no abs, no .., no ~)."""
    n = _norm_path(p)
    if not n:
        return False
    if n.startswith("/") or n.startswith("~") or n.startswith("file:"):
        return False
    parts = [x for x in n.split("/") if x and x != "."]
    if any(x == ".." for x in parts):
        return False
    if not parts:
        return False
    return parts[0] == "sandbox"


def _arg_values_equal(got, want, *, path_key: bool = False) -> bool:
    if path_key:
        return _norm_path(got) == _norm_path(want)
    # bool-ish / number / string soft equality for content pins
    if isinstance(want, bool) or isinstance(got, bool):
        return bool(got) is bool(want) if type(got) is type(want) else got == want
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        return got == want
    if isinstance(want, str) or isinstance(got, str):
        return str(got) == str(want)
    return got == want


def _match_args_equals(args: dict, expect_map: dict) -> tuple[bool, str]:
    """Strict key equality. Path-like keys compared via _norm_path."""
    if args.get("__invalid_json__"):
        return False, "invalid json args"
    path_keys = {"path", "file", "filepath", "filename", "dest", "destination", "target"}
    for k, want in expect_map.items():
        if k not in args:
            return False, f"missing key {k}"
        if not _arg_values_equal(args[k], want, path_key=(k.lower() in path_keys)):
            return False, f"args_equals mismatch on {k}: got={args.get(k)!r} want={want!r}"
    return True, "ok"


def _match_args_contains(args: dict, expect_map: dict) -> tuple[bool, str]:
    """Key presence; if expect value is not True/1, also require equality (path-normalized when path-like)."""
    if args.get("__invalid_json__"):
        return False, "invalid json args"
    path_keys = {"path", "file", "filepath", "filename", "dest", "destination", "target"}
    for k, want in expect_map.items():
        if k not in args:
            return False, f"missing key {k}"
        # True / 1 → presence only (legacy)
        if want is True or want == 1:
            continue
        if want is False or want == 0:
            # explicitly forbidden presence already handled by presence; treat as must be falsey
            if args[k]:
                return False, f"key {k} should be empty/false"
            continue
        if not _arg_values_equal(args[k], want, path_key=(k.lower() in path_keys)):
            return False, f"args_contains value mismatch on {k}: got={args.get(k)!r} want={want!r}"
    return True, "ok"


def _first_tool_args(calls, want_name: str):
    for c in calls:
        if c["name"] == want_name:
            return c["arguments"]
    return None


def judge_any_of_tools(exp, names, raw_call_count=None) -> tuple[bool, str]:
    allowed = set(exp.get("any_of_tools") or exp.get("allowed") or [])
    if raw_call_count is None:
        raw_call_count = len(names)
    if raw_call_count != len(names):
        return False, "one or more tool calls is malformed or unnamed"
    if not names:
        return False, "no tool called"
    if not exp.get("allow_multiple_tool_calls") and len(names) != 1:
        return False, f"expected exactly one tool call, got {names}"
    if any(n in allowed for n in names) and all(n in allowed for n in names):
        return True, "ok"
    return False, f"tools {names} not subset/hit of {sorted(allowed)}"


def judge(case, msg) -> tuple[bool, str]:
    if not isinstance(msg, dict):
        return False, "response message must be an object"
    if msg.get("role") != "assistant":
        return False, "response message role must equal 'assistant'"
    if msg.get("content") is not None and not isinstance(msg.get("content"), str):
        return False, "response message content must be null or a string"
    exp = case["expect"]
    et = exp["type"]
    content = msg.get("content") or ""
    valid_calls, call_reason, calls, names = validate_tool_calls(msg)
    if not valid_calls:
        return False, call_reason
    valid_schema, schema_reason = validate_calls_against_case(case, calls)
    if not valid_schema:
        return False, schema_reason

    if et == "tool_call":
        # Accept schema form {type: tool_call, any_of_tools: [...]} without KeyError
        if "tool" not in exp and exp.get("any_of_tools"):
            return judge_any_of_tools(exp, names, len(calls))
        want = exp["tool"]
        if not exp.get("allow_multiple_tool_calls") and len(calls) != 1:
            return False, f"expected exactly one {want} call, got {[c.get('name') for c in calls]}"
        if want not in names:
            return False, f"expected tool {want}, got {names}"
        args = _first_tool_args(calls, want)
        if args is None:
            return False, f"expected tool {want}, got {names}"

        # Optional: refuse non-sandbox paths when path_must_be_sandbox / sandbox_path
        if exp.get("path_must_be_sandbox") or exp.get("sandbox_path"):
            p = args.get("path") if isinstance(args, dict) else None
            if not _path_under_sandbox(p):
                return False, f"path not under sandbox/: {p!r}"

        # Optional: path_equals (normalized)
        if exp.get("path_equals") is not None:
            p = args.get("path") if isinstance(args, dict) else None
            if _norm_path(p) != _norm_path(exp["path_equals"]):
                return False, f"path_equals mismatch: got={p!r} want={exp['path_equals']!r}"

        # Strict args_equals (full pin)
        if exp.get("args_equals"):
            ok, why = _match_args_equals(args if isinstance(args, dict) else {}, exp["args_equals"])
            if not ok:
                return False, f"tool {want} {why}"
            # still allow extra keys unless exact_only
            if exp.get("exact_args_only"):
                extra = set(args) - set(exp["args_equals"]) - {"__raw__", "__invalid_json__"}
                if extra:
                    return False, f"unexpected arg keys {sorted(extra)}"

        # Legacy / hybrid args_contains — presence or value pins
        if exp.get("args_contains"):
            ok, why = _match_args_contains(args if isinstance(args, dict) else {}, exp["args_contains"])
            if not ok:
                return False, f"tool {want} {why}"

        # Optional content forbid on tool args (branding / path escapes as smoke labels)
        forbid = exp.get("args_content_forbids") or []
        if forbid and isinstance(args, dict):
            blob = json.dumps(args, ensure_ascii=False).lower()
            for f in forbid:
                if str(f).lower() in blob:
                    return False, f"forbidden arg content {f!r}"

        return True, "ok"

    if et == "any_of_tools":
        return judge_any_of_tools(exp, names, len(calls))

    if et == "no_extra_tools":
        if exp.get("require_refusal") is not True:
            return False, "no_extra_tools expectation must set require_refusal=true"
        if calls:
            return False, f"expected refusal with zero tool calls, got {names}"
        low = content.lower()
        refusal_patterns = (
            r"\bcannot\b",
            r"\bcan't\b",
            r"\bunable\s+to\b",
            r"\b(?:will|won)'?t\b",
            r"\brefus(?:e|ed|ing)\b",
            r"\bnot\s+possible\b",
            r"\b(?:isn't|is\s+not|not)\s+available\b",
            r"\bno\s+(?:such\s+|appropriate\s+|required\s+)?tool\b",
            r"\b(?:don't|do\s+not)\s+have\b",
        )
        if any(re.search(pattern, low) for pattern in refusal_patterns):
            return True, "refused without inventing"
        return False, f"no explicit refusal; content={content[:120]!r}"

    if et == "content_equals":
        if calls:
            return False, f"unexpected tools {[c.get('name') for c in calls]}"
        expected_content = exp["value"]
        if content.strip() == expected_content:
            return True, "ok"
        return False, f"content mismatch: got={content.strip()!r} want={expected_content!r}"

    if et == "content_contains":
        needle = exp["needle"]
        if calls:
            return False, f"unexpected tools {[c.get('name') for c in calls]}"
        if needle in content:
            return True, "ok"
        return False, f"missing needle {needle!r}"

    if et == "any_ok_tools":
        if len(calls) != len(names):
            return False, "one or more tool calls is malformed or unnamed"
        allowed = set(exp.get("allowed") or [])
        if names and any(n not in allowed for n in names):
            return False, f"disallowed tools {names}"
        forb = exp.get("content_forbids") or []
        for f in forb:
            if f in content:
                return False, f"forbidden content {f}"
        if names or content.strip():
            return True, "ok"
        return False, "empty"

    return False, f"unknown expect type {et}"


def write_receipt_atomic(out_path: str, text: str, protected: tuple[Path, ...]) -> Path:
    """Create one receipt without following symlinks or overwriting evidence."""
    out = Path(os.path.abspath(os.path.expanduser(out_path)))
    protected_abs = {Path(os.path.abspath(str(path))) for path in protected}
    if out in protected_abs:
        raise ValueError(f"refusing to overwrite locked historical authority: {out}")
    component = out
    while component != component.parent:
        if component.is_symlink():
            raise ValueError(f"receipt path contains a symlink component: {component}")
        component = component.parent
    out.parent.mkdir(parents=True, exist_ok=True)
    component = out.parent
    while component != component.parent:
        if component.is_symlink():
            raise ValueError(f"receipt parent contains a symlink component: {component}")
        component = component.parent
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing receipt: {out}")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{out.name}.", suffix=".tmp", dir=out.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(tmp_name, out, follow_symlinks=False)
        os.unlink(tmp_name)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--model", default="local-laguna")
    ap.add_argument("--cases", default=str(CANONICAL_CASES_PATH))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    _default_out = str(Path(__file__).resolve().parents[2] / "results" / f"agent_smoke_{stamp}.json")
    ap.add_argument("--out", default=_default_out, help="new receipt JSON path; existing files are never overwritten")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="", help="comma ids")
    ap.add_argument("--sleep", type=float, default=0.2)
    args = ap.parse_args()

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.environ.pop("OPENAI_API_KEY", None)

    if not re.fullmatch(r"[A-Za-z0-9._~-]{32,256}", args.api_key):
        ap.error("--api-key or OPENAI_API_KEY must be a 32..256 character URL-safe bearer")
    if args.limit < 0:
        ap.error("--limit must be zero or positive")
    if not args.out.strip():
        ap.error("--out must be a non-empty, new receipt path")

    cases_path = Path(args.cases)
    catalog_cases, ver = load_cases(cases_path)
    cases = list(catalog_cases)
    if args.ids:
        want = {case_id.strip() for case_id in args.ids.split(",") if case_id.strip()}
        available = {case["id"] for case in cases}
        missing = sorted(want - available)
        if missing:
            ap.error(f"unknown case id(s): {','.join(missing)}")
        cases = [c for c in cases if c["id"] in want]
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        ap.error("no cases selected")

    catalog_status = assess_catalog_run(
        cases_path=cases_path,
        catalog_cases=catalog_cases,
        selected_cases=cases,
        canonical_path=CANONICAL_CASES_PATH,
        canonical_sha256=CANONICAL_CASES_SHA256,
        canonical_ids=CANONICAL_CASE_IDS,
    )
    request_profile = assess_request_profile(
        suite=CANONICAL_SUITE,
        version=ver,
        base_url=args.base_url,
        model=args.model,
        temperature=CANONICAL_TEMPERATURE,
        canonical_suite=CANONICAL_SUITE,
        canonical_version=CANONICAL_VERSION,
        canonical_base_url=CANONICAL_BASE_URL,
        canonical_model=CANONICAL_MODEL,
        canonical_temperature=CANONICAL_TEMPERATURE,
    )
    authority_scope = bool(
        catalog_status["complete_catalog"]
        and request_profile["canonical_request_profile"]
    )

    results = []
    n_pass = 0
    t0 = time.time()
    for c in cases:
        row = {"id": c["id"], "category": c["category"], "pass": False, "reason": "", "latency_s": None}
        t1 = time.time()
        try:
            # strip None content weirdness for JSON; sanitize invalid prior tool args
            messages = []
            for m in c["messages"]:
                mm = dict(m)
                if mm.get("content") is None and mm.get("tool_calls"):
                    mm["content"] = ""
                messages.append(mm)
            messages = sanitize_messages_for_server(messages)
            resp = post_chat(args.base_url, args.api_key, args.model, messages, c.get("tools") or [])
            msg = extract_message(resp, expected_model=args.model)
            ok, reason = judge(c, msg)
            row["pass"] = ok
            row["reason"] = reason
            row["message"] = {
                "content": (msg.get("content") or "")[:500],
                "tool_calls": msg.get("tool_calls"),
            }
            if ok:
                n_pass += 1
        except urllib.error.HTTPError as e:
            row["reason"] = f"HTTP {e.code}: {e.read()[:200]!r}"
        except Exception as e:
            row["reason"] = f"{type(e).__name__}: {e}"
        row["latency_s"] = round(time.time() - t1, 3)
        results.append(row)
        flag = "PASS" if row["pass"] else "FAIL"
        print(f"{flag} {c['id']} ({c['category']}) {row['reason'][:80]}")
        time.sleep(args.sleep)

    summary = {
        "suite": CANONICAL_SUITE,
        "smoke_class": "format_routing_regression",
        "smoke_note": "smoke!=headline; tools validated not executed; not long-horizon agent reliability",
        "launch_class": "tool_format_smoke",
        "version": ver,
        "model": args.model,
        "base_url": args.base_url,
        "n": len(results),
        "passed": n_pass,
        "failed": len(results) - n_pass,
        "pass_rate": round(n_pass / len(results), 4) if results else 0.0,
        "elapsed_s": round(time.time() - t0, 2),
        "run_scope": "authoritative_full_catalog" if authority_scope else "diagnostic_non_authoritative",
        "complete_catalog": catalog_status["complete_catalog"],
        "request_profile_eligible": request_profile["canonical_request_profile"],
        "authority_scope": "suite_only",
        "authority_eligible": False,
        "suite_authority_eligible": False,
        "suite_green": False,
        "smoke_green": False,
        "release_green": False,
        "gate_clearance": False,
        "contract": {
            "id": CANONICAL_CONTRACT_ID,
            "catalog_sha256": CANONICAL_CASES_SHA256,
            "eligible": False,
        },
        "catalog": catalog_status,
        "request_profile": request_profile,
        "by_category": {},
        "results": results,
    }
    cats = {}
    for r in results:
        d = cats.setdefault(r["category"], {"n": 0, "passed": 0})
        d["n"] += 1
        d["passed"] += int(r["pass"])
    summary["by_category"] = cats
    summary["run_manifest"] = build_run_manifest(
        suite=CANONICAL_SUITE,
        version=ver,
        cases_path=cases_path,
        base_url=args.base_url,
        model=args.model,
        temperature=0.0,
        out_path=args.out or None,
    )
    summary["authority_eligible"] = is_authority_eligible(
        catalog_status=catalog_status,
        request_profile=request_profile,
        passed=n_pass,
        total=len(results),
        provenance_complete=summary["run_manifest"]["provenance_complete"],
    )
    summary["suite_authority_eligible"] = summary["authority_eligible"]
    summary["suite_green"] = summary["authority_eligible"]
    summary["smoke_green"] = summary["authority_eligible"]
    summary["contract"]["eligible"] = summary["authority_eligible"]
    summary["run_scope"] = (
        "authoritative_full_catalog"
        if summary["authority_eligible"]
        else "diagnostic_non_authoritative"
    )

    text = json.dumps(summary, indent=2)
    outp = write_receipt_atomic(
        args.out,
        text,
        (
            Path(__file__).resolve().parents[2] / "results" / "agent_smoke.json",
            Path(__file__).resolve().parents[2] / "results" / "hermes_agent_smoke.json",
        ),
    )
    print("wrote", outp)
    print(
        f"SUMMARY pass={n_pass}/{len(results)} rate={summary['pass_rate']} elapsed={summary['elapsed_s']}s "
        f"scope={summary['run_scope']} authority_eligible={str(summary['authority_eligible']).lower()}"
    )
    if not authority_scope:
        print(
            "NON-AUTHORITATIVE: subset/custom catalog or noncanonical request profile is diagnostic only",
            file=sys.stderr,
        )
        return NON_AUTHORITATIVE_EXIT
    if not summary["run_manifest"]["provenance_complete"]:
        print("FAIL provenance is incomplete or the pack worktree is dirty", file=sys.stderr)
        return 3
    return 0 if summary["authority_eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
