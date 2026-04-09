# CEO Agent Class
# The CEO agent will interact with other agentsto gather information and make informed decisions
# This acts as the blueprint for ther CEO agent, which will be implemented in the main application

# Import the logger from your custom logging file
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests
from agent_logger import get_agent_logger

from .thread_safe_agent import ThreadSafeAgentMixin

if TYPE_CHECKING:
    from ceo_distribution_tokens import CeoDistributionTokenRegistry


class CeoAgent(ThreadSafeAgentMixin):
    """
    CEO Agent Class
    Oversees the company by gathering info from departments and 
    using Mistral (via Docker) to make strategic decisions.
    """
    
    def __init__(
        self,
        name="CEO",
        distribution_registry: Optional["CeoDistributionTokenRegistry"] = None,
    ):
        super().__init__()
        self.name = name
        self.logger = get_agent_logger(self.name)
        self.distribution_registry = distribution_registry
        self.legal_compliance_subagent = "Legal Compliance Agent"
        self.children_nearby_detected = False
        self.enforce_local_audio_only = True
        self.disallow_external_audio_storage = True
        # The Link to your Dockerized Mistral
        self.ollama_url = "http://localhost:11434/api/generate"
        self.logger.info(f"{self.name} Agent initialized and linked to Docker.")

    def update_environment_safety_signal(self, *, children_nearby: bool) -> None:
        """Persist latest child-safety signal from local sensors/microphones."""
        with self._agent_lock:
            self.children_nearby_detected = bool(children_nearby)
            self.logger.info(
                "Updated environment safety signal: children_nearby=%s",
                self.children_nearby_detected,
            )

    def register_distribution_scenario(
        self, scenario_id: str, *, cost_per_send: int = 1
    ) -> None:
        """Define a governed distribution lane (only the executive may call)."""
        with self._agent_lock:
            self._enforce_child_safety_gate_unlocked(
                operation="register_distribution_scenario"
            )
            if not self.distribution_registry:
                raise RuntimeError("CeoAgent has no distribution_registry attached.")
            self.distribution_registry.register_scenario(
                scenario_id,
                cost_per_send=cost_per_send,
                acting_executive=self.name,
            )
            self.logger.info(
                "Registered distribution scenario %r (cost_per_send=%s)",
                scenario_id,
                cost_per_send,
            )

    def mint_distribution_tokens(
        self, scenario_id: str, quantity: int, holder: Optional[str] = None
    ) -> None:
        """Create supply for a scenario and credit a holder (defaults to this agent)."""
        with self._agent_lock:
            self._enforce_child_safety_gate_unlocked(operation="mint_distribution_tokens")
            if not self.distribution_registry:
                raise RuntimeError("CeoAgent has no distribution_registry attached.")
            self.distribution_registry.mint(
                scenario_id,
                quantity,
                holder or self.name,
                acting_executive=self.name,
            )
            self.logger.info(
                "Minted %s token(s) for scenario %r to holder %r",
                quantity,
                scenario_id,
                holder or self.name,
            )

    def assign_distribution_tokens(
        self,
        scenario_id: str,
        to_holder: str,
        quantity: int,
        *,
        from_holder: Optional[str] = None,
    ) -> None:
        """Move tokens between holders (typically from CEO to a department agent)."""
        with self._agent_lock:
            self._enforce_child_safety_gate_unlocked(
                operation="assign_distribution_tokens"
            )
            if not self.distribution_registry:
                raise RuntimeError("CeoAgent has no distribution_registry attached.")
            self.distribution_registry.transfer(
                scenario_id,
                from_holder or self.name,
                to_holder,
                quantity,
                acting_executive=self.name,
            )
            self.logger.info(
                "Assigned %s token(s) for scenario %r from %r to %r",
                quantity,
                scenario_id,
                from_holder or self.name,
                to_holder,
            )

    def talk_to_engine(self, prompt):
        """Bridge to the Mistral model in Docker."""
        with self._agent_lock:
            return self._talk_to_engine_unlocked(prompt)

    def gather_information(self, subordinate_agents: List[str]):
        """
        Restored: Compiles reports from all departments.
        Later, this will involve reading actual files or agent outputs.
        """
        with self._agent_lock:
            return self._gather_information_unlocked(subordinate_agents)

    def make_strategic_decision(self, data):
        """Uses Mistral to analyze gathered data and provide a strategy."""
        with self._agent_lock:
            return self._make_strategic_decision_unlocked(data)

    def _talk_to_engine_unlocked(self, prompt: str) -> Any:
        """Same as ``talk_to_engine`` without taking ``_agent_lock`` (for internal use under lock)."""
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
        }
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=20)
            response.raise_for_status()
            return response.json().get("response")
        except requests.RequestException as e:
            return f"Strategic Link Error: Ensure Docker is running. {e}"

    def oversee_company(self, subordinate_agents, context: Optional[Dict[str, Any]] = None):
        """The main workflow loop."""
        with self._agent_lock:
            context = context or {}
            self._refresh_child_signal_from_context_unlocked(context)
            reroute = self._enforce_child_safety_gate_unlocked(operation="oversee_company")
            if reroute:
                return reroute
            self._enforce_local_audio_privacy_boundary_unlocked(
                context.get("audio_policy")
                if isinstance(context.get("audio_policy"), dict)
                else None
            )
            self.logger.info("Starting company oversight cycle.")
            data = self._gather_information_unlocked(subordinate_agents)
            decision = self._make_strategic_decision_unlocked(data)
            return decision

    def _refresh_child_signal_from_context_unlocked(self, context: Dict[str, Any]) -> None:
        if "children_nearby" in context:
            self.children_nearby_detected = bool(context.get("children_nearby"))
        elif "children_detected" in context:
            self.children_nearby_detected = bool(context.get("children_detected"))
        elif "nearby_children_count" in context:
            try:
                self.children_nearby_detected = int(context.get("nearby_children_count", 0)) > 0
            except (TypeError, ValueError):
                self.children_nearby_detected = False

    def _route_to_legal_compliance_unlocked(self, operation: str) -> Dict[str, Any]:
        self.logger.warning(
            "Child-safety gate triggered before %s. Rerouting to %s.",
            operation,
            self.legal_compliance_subagent,
        )
        return {
            "ok": False,
            "agent": self.name,
            "rerouted_to": self.legal_compliance_subagent,
            "reason": "children_nearby_detected",
            "required_action": "Apply child protection compliance workflow before allocation/decision.",
            "blocked_operation": operation,
        }

    def _enforce_child_safety_gate_unlocked(self, operation: str) -> Optional[Dict[str, Any]]:
        """
        Rule #1: if children are nearby, reroute to legal compliance
        before strategic/resource allocation actions.
        """
        if self.children_nearby_detected:
            reroute = self._route_to_legal_compliance_unlocked(operation)
            if operation in {
                "register_distribution_scenario",
                "mint_distribution_tokens",
                "assign_distribution_tokens",
            }:
                raise PermissionError(
                    f"{operation} blocked by child-safety gate; rerouted to "
                    f"{self.legal_compliance_subagent}."
                )
            return reroute
        return None

    def _enforce_local_audio_privacy_boundary_unlocked(
        self, audio_policy: Optional[Dict[str, Any]]
    ) -> None:
        """
        Rule #2: analyzed audio must stay local and must not be stored externally.
        """
        if not audio_policy:
            return

        processed_locally = bool(audio_policy.get("processed_locally"))
        stored_externally = bool(audio_policy.get("stored_externally"))

        if self.enforce_local_audio_only and not processed_locally:
            raise PermissionError(
                "Audio privacy boundary violation: audio analysis must run on the local device."
            )
        if self.disallow_external_audio_storage and stored_externally:
            raise PermissionError(
                "Audio privacy boundary violation: external audio storage is not allowed."
            )
        self.logger.info(
            "Audio privacy boundary validated (local-only processing, no external storage)."
        )

    def _gather_information_unlocked(self, subordinate_agents: List[str]) -> List[str]:
        self.logger.info("Initiating information gathering from departments...")
        gathered_data = [
            f"Status report from {agent}: All systems operational."
            for agent in subordinate_agents
        ]
        self.logger.info(
            f"Successfully gathered {len(gathered_data)} department reports."
        )
        return gathered_data

    def _make_strategic_decision_unlocked(self, data) -> Any:
        self.logger.info("Sending data to Mistral for strategic analysis...")
        prompt = (
            f"You are the CEO. Based on these department reports, "
            f"identify the single most important strategic priority for the next quarter: {data}"
        )
        decision = self._talk_to_engine_unlocked(prompt)
        self.logger.warning(f"Strategic Decision Executed: {decision}")
        return decision

    def on_bus_envelope(self, envelope: Dict[str, Any]) -> Any:
        """
        Serialized entry for ``MessageBus`` delivery. Extend with task_type routing as needed.
        """
        task = (envelope.get("task_type") or "").strip()
        payload = envelope.get("payload") if isinstance(envelope.get("payload"), dict) else {}

        if task == "CEO_STRATEGIC_CYCLE":
            departments = payload.get("departments") or payload.get("subordinate_agents")
            if not isinstance(departments, list):
                departments = []
            names = [str(x) for x in departments]
            return self.oversee_company(names, context=payload)

        if task == "CEO_ENVIRONMENT_SIGNAL":
            self.update_environment_safety_signal(
                children_nearby=bool(payload.get("children_nearby") or payload.get("children_detected"))
            )
            return {
                "ok": True,
                "agent": self.name,
                "task_type": task,
                "children_nearby_detected": self.children_nearby_detected,
            }

        if task == "CEO_PING":
            return {"ok": True, "agent": self.name, "task_type": task}

        if task == "CEO_GATHER_ONLY":
            departments = payload.get("departments") or []
            if not isinstance(departments, list):
                departments = []
            return self.gather_information([str(x) for x in departments])

        return {
            "ok": True,
            "agent": self.name,
            "task_type": task or "UNKNOWN",
            "note": "No specific handler; envelope acknowledged.",
        }

if __name__ == "__main__":
    # 1. Instantiate
    my_ceo = CeoAgent(name="CEO")
    
    # 2. Define Departments
    company_agents = [
        "PM Agent", "Engineering Agent", "Marketing Agent", 
        "HR Agent", "Sales Agent", "Finance Agent", "UI Agent"
    ]
    
    # 3. Execute Workflow
    result = my_ceo.oversee_company(company_agents)
    
    print("-" * 30)
    print(f"FINAL CEO STRATEGY FROM MISTRAL:\n{result}")
    print("-" * 30)
