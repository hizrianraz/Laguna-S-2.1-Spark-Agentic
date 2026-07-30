#!/usr/bin/python3 -I
"""Hermes-class / tool-agent compatible sample client for local Laguna serve.

Wording: OpenAI-compatible tool-calling shape used by Hermes-class agent runtimes.
This is NOT a Nous Research endorsement and not Hermes Agent product code.

Usage:
  export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
  export OPENAI_API_KEY="$LAGUNA_API_KEY"
  /usr/bin/python3 -I -S hermes/sample_client.py
"""

from __future__ import annotations

import json
import os
import re
import resource
import sys
import urllib.error
import urllib.request

NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = os.environ.get("OPENAI_MODEL", "local-laguna")
os.environ.pop("OPENAI_API_KEY", None)
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


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
    return json.loads(raw, parse_constant=_reject_json_constant, object_pairs_hook=_unique_json_object)

# Minimal tool schema — agent runtimes should pass the real catalog.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Return the current UTC time as ISO-8601.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone, default UTC",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc",
            "description": "Evaluate a basic arithmetic expression with + - * / and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
            },
        },
    },
]


def chat(messages, tools=None, temperature=0.0, max_tokens=512):
    body = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools is not None:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "laguna-spark-hermes-sample/0.1",
        },
        method="POST",
    )
    with NO_PROXY_OPENER.open(req, timeout=300) as resp:
        return parse_json_strict(resp.read().decode())


def main():
    if BASE_URL != "http://127.0.0.1:8000/v1" or MODEL != "local-laguna":
        print("sample client is restricted to the loopback local-laguna launch profile", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[A-Za-z0-9._~-]{32,256}", API_KEY):
        print("OPENAI_API_KEY must be the 32..256 character URL-safe Laguna bearer", file=sys.stderr)
        return 2
    print(f"base_url={BASE_URL} model={MODEL}")
    try:
        models = parse_json_strict(NO_PROXY_OPENER.open(
            urllib.request.Request(
                f"{BASE_URL}/models",
                headers={"Authorization": f"Bearer {API_KEY}"},
            ),
            timeout=30,
        ).read().decode())
        rows = models.get("data") if isinstance(models, dict) else None
        if not isinstance(rows, list) or len(rows) != 1 or rows[0].get("id") != MODEL:
            raise ValueError("model inventory does not contain exactly local-laguna")
        print(f"models_ok={MODEL}")
    except Exception as e:
        print("models probe failed:", e, file=sys.stderr)
        return 2

    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful tool-using assistant. "
                "Only call tools from the provided schema. "
                "Never invent tool names. Prefer short answers."
            ),
        },
        {
            "role": "user",
            "content": "What is (17+4)*3? Use the calc tool, then answer briefly.",
        },
    ]
    try:
        out = chat(messages, tools=TOOLS)
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read()[:500], file=sys.stderr)
        return 1
    except Exception as e:
        print("request failed:", e, file=sys.stderr)
        return 1

    if out.get("model") != MODEL or not isinstance(out.get("choices"), list) or len(out["choices"]) != 1:
        print("response identity/choice count mismatch", file=sys.stderr)
        return 1
    msg = out["choices"][0].get("message")
    if not isinstance(msg, dict) or msg.get("role") != "assistant":
        print("response message shape mismatch", file=sys.stderr)
        return 1
    print(json.dumps(msg, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
