import uuid
import datetime
from agent_logger import get_agent_logger, log_inter_agent_message

class AdvisorAgent:
    """
    Advisor Agent Class
    Responsible for auditing the CEO's decisions and ensuring all actions 
    align with the company's established strategic guidelines.
    """
    
    def __init__(self, name="Strategic Advisor", core_strategy=""):
        self.name = name
        self.core_strategy = core_strategy
        self.logger = get_agent_logger(self.name)
        self.logger.info(f"{self.name} initialized with core strategy: '{self.core_strategy[:50]}...'")

    def evaluate_ceo_decision(self, ceo_proposal_message):
        """
        Takes a JSON message from the CEO, evaluates the payload against the 
        core strategy, and returns an advisory response message.
        """
        self.logger.info("Received proposal from CEO for strategic review.")
        
        # 1. Log the incoming message from the CEO
        log_inter_agent_message(self.logger, ceo_proposal_message, direction="RECEIVING")
        
        # Extract the CEO's proposed payload to analyze
        proposed_action = ceo_proposal_message.get("payload", {})
        task_type = ceo_proposal_message.get("task_type", "UNKNOWN")
        
        # 2. Perform the evaluation (Simulated AI Logic)
        # In a real app, you would pass the self.core_strategy and the proposed_action to an LLM prompt here.
        is_aligned = True
        feedback = "Proposal strongly aligns with Q1/Q2 revenue targets."
        
        # Example of catching a strategic drift:
        if "hardware" in str(proposed_action).lower() and "SaaS" in self.core_strategy:
            is_aligned = False
            feedback = "WARNING: Proposed hardware expansion violates the core SaaS focus strategy."

        # 3. Construct the Advisor's response using the strict JSON schema
        advisory_response = {
            "id": f"adv-{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "sender": self.name,
            "recipient": ceo_proposal_message.get("sender", "CEO"),
            "task_type": "STRATEGY_REVIEW_RESULT",
            "context": {
                "original_task": task_type,
                "review_cycle": "pre-execution"
            },
            "payload": {
                "is_aligned": is_aligned,
                "assessment": feedback,
                "recommended_action": "PROCEED" if is_aligned else "REVISE"
            },
            "status": "done",
            "error": ""
        }
        
        # 4. Log the outgoing feedback
        log_inter_agent_message(self.logger, advisory_response, direction="SENDING")
        
        return advisory_response