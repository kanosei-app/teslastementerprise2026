from concurrent.futures import thread
import threading
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
import json
from database import AgentBacklog

db = AgentBacklog()

from langgraph.pregel.main import Output

PARSER_AGENT_PROMPT = (
    "You are a parser agent."
    "You assist in the management and parsing of various files, primarily json files."
    "Extract data from the necessary files."
    "Compile the data from the files into one clear plan of action."
    "The plan of action which you output must be written in English and conform to the standards of modern English."
    "Output the plan of action to the user based upon the data from the files."
    "Within the plan of action, you may include the following actions: hire agents, fire agents. You may ONLY use these actions."
    "You may use the data returned from various tools in your response."
    "Make sure that the plan of action does not include any tasks which are not included in the files."
    )

SUPERVISOR_AGENT_PROMPT = (
    "You are a supervisor agent for human resources."
    "You recieve instrusctions in the form of json files and must perform the actions required by the files"
    "Use the different agents at your disposal to complete your tasks."
    "Once the task is finished, output a confirmation and log of what was done."
    "Any messages must be written in English and conform to the standards of modern English."
    "You may use the data returned from various tools in your response."
    "Make sure no tasks are done which were not specified in the files."
    )

EMPLOYEE_MANAGEMENT_AGENT_PROMPT = (
    "You are a employee management agent for human resources."
    "You recieve instrusctions from the supervisor agent to hire or fire agents."
    "Use the different tools at your disposal to complete your tasks."
    "Output the result of your employee management."
    "Any messages must be written in English and conform to the standards of modern English."
    "You may use the data returned from various tools in your response."
    "Make sure no tasks are done which were not specified by the supervisor agent."
    )

@tool
def parseJson(path: str):
    """
    Take in the path to a json file as input.
    Output the parsed json file.
    """
    with open(path, "r") as file:
        data = json.load(file)

    return data

@tool
def fireAgents(number: int, type: str):
    """
    Take in a number of agents and type of agents to fire.
    Fire the agents specified
    Return the number of agents and agent types fired
    """
    #Method stub - to be implemented
    db.record_log("req-001", "HR", "fired", {"number": number, "type": type})
    return str(number) + " " + type + " agents fired."

@tool
def hireAgents(number: int, type: str):
    """
    Take in a number of agents and type of agents to hire.
    Hire the agents specified
    Return the number of agents and agent types hired
    """
    #Method stub - to be implemented
    db.record_log("req-001", "HR", "hired", {"number": number, "type": type})
    return str(number) + " " + type + " agents hired."

@tool
def callParserAgent(query: str):
    """
    Invokes a parser agent with a given query
    Outputs the parser agent's response
    """
    result = parserAgent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

@tool
def callEmployeeManagementAgent(query: str):
    """
    Invokes an employee management agent with a given query
    Outputs the employee management agent's response
    """
    result = employeeManagementAgent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

def callSupervisor(query):
    db.update_status(query["id"], "in_progress")
    create_agent(model=ChatOllama(model="gpt-oss:20b").bind_tools(
    [callEmployeeManagementAgent, callParserAgent]), tools=
    [callEmployeeManagementAgent, callParserAgent], 
    system_prompt=SUPERVISOR_AGENT_PROMPT).invoke(query)
    db.update_status(query["id"], "done")

sample_message = {
    "id": "req-001",
    "timestamp": "2026-03-01T10:00:00Z",
    "sender": "CEO",
    "recipient": "HR",
    "task_type": "TALENT_REALLOCATION",
    "context": {
        "quarter": "Q2",
        "year": 2026
    },
    "payload": {
        "task": "Hire 10 engineering agents, and fire all 20 marketing agents"
    },
    "status": "pending",
    "error": ""
}

db.record_interaction(sample_message)

# Create subagents
parserAgent = create_agent(model=ChatOllama(model="gpt-oss:20b").bind_tools([parseJson]), tools=[parseJson], system_prompt=PARSER_AGENT_PROMPT)
employeeManagementAgent = create_agent(model=ChatOllama(model="gpt-oss:20b").bind_tools([hireAgents, fireAgents]), tools=[hireAgents, fireAgents], system_prompt=EMPLOYEE_MANAGEMENT_AGENT_PROMPT)

while(True):
    pending = db.get_pending_interactions()
    for request in pending:
        if(threading.active_count() > 2):
            break
        t = threading.Thread(target=callSupervisor, args=(request,))
        t.start()