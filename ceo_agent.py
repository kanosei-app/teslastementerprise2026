# CEO Agent Class
# The CEO agent will interact with other agentsto gather information and make informed decisions
# This acts as the blueprint for ther CEO agent, which will be implemented in the main application

# Import the logger from your custom logging file
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests
from agent_logger import get_agent_logger
from thread_safe_agent import ThreadSafeAgentMixin

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
        # The Link to your Dockerized Mistral
        self.ollama_url = "http://localhost:11434/api/generate"
        self.logger.info(f"{self.name} Agent initialized and linked to Docker.")

    def register_distribution_scenario(
        self, scenario_id: str, *, cost_per_send: int = 1
    ) -> None:
        """Define a governed distribution lane (only the executive may call)."""
        with self._agent_lock:
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
            response = requests.post(self.ollama_url, json=payload)
            return response.json().get("response")
        except Exception as e:
            return f"Strategic Link Error: Ensure Docker is running. {e}"

    def oversee_company(self, subordinate_agents):
        """The main workflow loop."""
        with self._agent_lock:
            self.logger.info("Starting company oversight cycle.")
            data = self._gather_information_unlocked(subordinate_agents)
            decision = self._make_strategic_decision_unlocked(data)
            return decision

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
            return self.oversee_company(names)

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