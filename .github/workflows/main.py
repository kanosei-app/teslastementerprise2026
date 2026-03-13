import json
import uuid
import datetime
import subprocess
from pathlib import Path
from crewai import Agent, Task
from crewai.llm import LLM

# Local LLM (Ollama)
llm = LLM(model="llama3")

def now():
    return datetime.datetime.utcnow().isoformat()

def make_response(sender, recipient, task_type, payload, status="done", error=None):
    return {
        "id": str(uuid.uuid4()),
        "timestamp": now(),
        "sender": sender,
        "recipient": recipient,
        "task_type": task_type,
        "context": "",
        "payload": payload,
        "status": status,
        "error": error
    }

class EngineeringAgent:
    def __init__(self):
        self.name = "engineering_agent"
        self.agent = Agent(
            role="Engineering Agent",
            goal="Write and maintain high‑quality code based on product specs.",
            backstory="You are the engineering team of a virtual company.",
            llm=llm
        )

    def generate_code(self, spec):
        prompt = f"Write clean, minimal code for the following requirement:\n\n{spec}\n\nReturn ONLY code."
        result = self.agent.run(prompt)
        return result

    def write_to_repo(self, file_path, content):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path)

    def handle_message(self, message):
        task_type = message["task_type"]
        payload = message["payload"]

        try:
            if task_type == "generate_code":
                code = self.generate_code(payload["spec"])
                file_path = payload.get("repo_path", "generated/code.py")
                saved_path = self.write_to_repo(file_path, code)

                return make_response(
                    sender=self.name,
                    recipient=message["sender"],
                    task_type=task_type,
                    payload={"file_path": saved_path, "code": code}
                )

            else:
                return make_response(
                    sender=self.name,
                    recipient=message["sender"],
                    task_type=task_type,
                    payload={},
                    status="error",
                    error=f"Unknown task_type: {task_type}"
                )

        except Exception as e:
            return make_response(
                sender=self.name,
                recipient=message["sender"],
                task_type=task_type,
                payload={},
                status="error",
                error=str(e)
            )

if __name__ == "__main__":
    import sys
    raw = sys.stdin.read()
    message = json.loads(raw)
    agent = EngineeringAgent()
    response = agent.handle_message(message)
    print(json.dumps(response, indent=2))
