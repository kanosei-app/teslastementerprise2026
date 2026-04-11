"""
Single source of truth for enterprise persistence.

- **SQLite** — internal backlog: ``AgentBacklog`` / ``MessageBus`` (``ENTERPRISE_BACKLOG_DB``).
- **JSONL** — bus audit file (``ENTERPRISE_MESSAGE_BUS_JSONL``).
- **MongoDB** — inter-agent HTTP/API hub (``MONGO_URI``, ``ENTERPRISE_MONGO_INTER_AGENT_DB``); see ``inter_agent_mongo.py``.

ENTERPRISE_BACKLOG_DB            — SQLite path (default: <repo>/enterprise_backlog.db)
ENTERPRISE_MESSAGE_BUS_JSONL     — JSONL path (default: <repo>/enterprise_message_bus.jsonl)
MONGO_URI                        — Mongo connection (default: mongodb://localhost:27017/)
ENTERPRISE_MONGO_INTER_AGENT_DB  — Mongo DB name (default: enterprise_inter_agent)
"""

from __future__ import annotations

import os

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


def backlog_db_path() -> str:
    env = os.environ.get("ENTERPRISE_BACKLOG_DB")
    if env:
        return os.path.abspath(env)
    return os.path.join(_REPO_ROOT, "enterprise_backlog.db")


def message_bus_jsonl_path() -> str:
    env = os.environ.get("ENTERPRISE_MESSAGE_BUS_JSONL")
    if env:
        return os.path.abspath(env)
    return os.path.join(_REPO_ROOT, "enterprise_message_bus.jsonl")


def inter_agent_mongo_uri() -> str:
    return os.environ.get("MONGO_URI", "mongodb://localhost:27017/")


def inter_agent_mongo_db_name() -> str:
    return os.environ.get("ENTERPRISE_MONGO_INTER_AGENT_DB", "enterprise_inter_agent")
