"""
HTTP helpers for inter-agent communication when agents live in separate services.

Expected server routes (example):
- POST /messages/send               body: envelope dict
- GET  /messages/receive/{agent}    returns one envelope or null
- GET  /messages/pending/{agent}    returns {"pending": int}
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests


def send_envelope_http(
    base_url: str,
    envelope: Dict[str, Any],
    *,
    timeout_s: float = 10.0,
) -> Dict[str, Any]:
    """Send one standardized envelope to a MessageBus HTTP service."""
    url = f"{base_url.rstrip('/')}/messages/send"
    resp = requests.post(url, json=envelope, timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object response from /messages/send")
    return data


def receive_envelope_http(
    base_url: str,
    agent_name: str,
    *,
    timeout_s: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """Pull one queued envelope for an agent from an HTTP-backed mailbox."""
    url = f"{base_url.rstrip('/')}/messages/receive/{agent_name}"
    resp = requests.get(url, timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ValueError("Expected object-or-null response from /messages/receive/{agent}")
    return data


def pending_count_http(
    base_url: str,
    agent_name: str,
    *,
    timeout_s: float = 10.0,
) -> int:
    """Read queued mailbox depth for an agent from an HTTP service."""
    url = f"{base_url.rstrip('/')}/messages/pending/{agent_name}"
    resp = requests.get(url, timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict) or "pending" not in data:
        raise ValueError("Expected {'pending': <int>} from /messages/pending/{agent}")
    return int(data["pending"])
