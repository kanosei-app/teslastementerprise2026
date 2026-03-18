# CEO Agent Class
# The CEO agent will interact with other agentsto gather information and make informed decisions
# This acts as the blueprint for ther CEO agent, which will be implemented in the main application

# Import the logger from your custom logging file
import requests
from agent_logger import get_agent_logger

class CeoAgent:
    """
    CEO Agent Class
    Oversees the company by gathering info from departments and 
    using Mistral (via Docker) to make strategic decisions.
    """
    
    def __init__(self, name="CEO"):
        self.name = name
        self.logger = get_agent_logger(self.name)
        # The Link to your Dockerized Mistral
        self.ollama_url = "http://localhost:11434/api/generate"
        self.logger.info(f"{self.name} Agent initialized and linked to Docker.")

    def talk_to_engine(self, prompt):
        """Bridge to the Mistral model in Docker."""
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            return response.json().get('response')
        except Exception as e:
            return f"Strategic Link Error: Ensure Docker is running. {e}"

    def gather_information(self, subordinate_agents):
        """
        Restored: Compiles reports from all departments.
        Later, this will involve reading actual files or agent outputs.
        """
        self.logger.info("Initiating information gathering from departments...")
        
        # Currently creating simulated reports for each department
        gathered_data = [f"Status report from {agent}: All systems operational." for agent in subordinate_agents]
        
        self.logger.info(f"Successfully gathered {len(gathered_data)} department reports.")
        return gathered_data

    def make_strategic_decision(self, data):
        """Uses Mistral to analyze gathered data and provide a strategy."""
        self.logger.info("Sending data to Mistral for strategic analysis...")
        
        # Packaging the gathered data into a professional prompt
        prompt = (
            f"You are the CEO. Based on these department reports, "
            f"identify the single most important strategic priority for the next quarter: {data}"
        )
        
        decision = self.talk_to_engine(prompt)
        self.logger.warning(f"Strategic Decision Executed: {decision}")
        return decision

    def oversee_company(self, subordinate_agents):
        """The main workflow loop."""
        self.logger.info("Starting company oversight cycle.")
        
        # 1. Gather (The Researcher)
        data = self.gather_information(subordinate_agents)
        
        # 2. Decide (The Brain - calls Docker)
        decision = self.make_strategic_decision(data)
        
        return decision

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