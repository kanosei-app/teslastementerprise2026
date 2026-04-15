from ._compat import import_legacy_ceo_agents_module

_legacy = import_legacy_ceo_agents_module("thread_safe_agent")
SupportsBusRegistration = _legacy.SupportsBusRegistration
ThreadSafeAgentMixin = _legacy.ThreadSafeAgentMixin

__all__ = ["SupportsBusRegistration", "ThreadSafeAgentMixin"]
