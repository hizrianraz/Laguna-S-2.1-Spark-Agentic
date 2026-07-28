#!/usr/bin/env python3
"""Hermes-class / tool-agent compatible sample client for local Laguna serve.

Wording: OpenAI-compatible tool-calling shape used by Hermes-class agent runtimes.
This is NOT a Nous Research endorsement and not Hermes Agent product code.

Usage:
  export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
  export OPENAI_API_KEY=sk-local
  python hermes/sample_client.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-local")
MODEL = os.environ.get("OPENAI_MODEL", "local-laguna")

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
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode())


def main():
    print(f"base_url={BASE_URL} model={MODEL}")
    try:
        models = urllib.request.urlopen(
            urllib.request.Request(
                f"{BASE_URL}/models",
                headers={"Authorization": f"Bearer {API_KEY}"},
            ),
            timeout=30,
        ).read()
        print("models:", models[:300].decode())
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

    msg = out["choices"][0]["message"]
    print(json.dumps(msg, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
