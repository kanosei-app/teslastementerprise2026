# Global Requirements

## Decision-Making Hierarchy: 
CEO Agent is the central decision-maker. It delegates tasks, resolves conflicts, approves major actions (e.g., budgets >$10K, product launches), and monitors progress via periodic reports from all agents.

# Agent Specific Info

## CEO Agent
- Role: Strategic leader; sets goals, delegates, arbitrates.
- Responsibilities: Analyze market trends; define quarterly OKRs; assign tasks (e.g., "Launch MVP"); review reports; veto/approve proposals.
- Inputs: Market data, agent reports. Outputs: Task delegations, OKRs, final decisions.
- Behaviors: Uses reasoning chains for prioritization; prompts like "Prioritize based on ROI >20%." Tools: Analytics dashboard, email notifier.

## Pseoudocode of CEO Flow

    PROCEDURE Execute_CEO_Reasoning_Loop(IncomingEvent)
    
        CurrentContext <- Retrieve_Agent_Memory()
        CompanyState <- Fetch_Dashboard_KPIs()
        
        PromptInput <- Combine_Data(IncomingEvent, CurrentContext, CompanyState)
        
        ReasoningResponse <- Prompt_LLM(PromptInput, "JSON_Format")
        
        ParsedPlan <- Extract_Plan(ReasoningResponse)
        
        Save_To_Memory(ParsedPlan.Thought)
        
        ActionResults <- Initialize_Empty_List()
        
        FOR EACH Action IN ParsedPlan.Actions DO
        
            SWITCH Action.Name DO
            
                CASE "DelegateTask":
                    Result <- Route_To_Agent(Action.Parameters.Department, Action.Parameters.Directive)
                    Append Result TO ActionResults
                    
                CASE "ReplanBudget":
                    Result <- Adjust_Financial_Parameters(Action.Parameters)
                    Append Result TO ActionResults
                    
                CASE "SummarizeCycle":
                    Result <- Generate_Executive_Report(Action.Parameters)
                    Append Result TO ActionResults
                    
                DEFAULT:
                    Result <- Log_Unknown_Action(Action.Name)
                    Append Result TO ActionResults
                    
            END SWITCH
            
        END FOR
        
        IF Requires_Further_Reasoning(ActionResults) IS TRUE THEN
            RETURN Execute_CEO_Reasoning_Loop(ActionResults)
        END IF
        
        Update_Dashboard_Status("Idle", ParsedPlan.Thought)
        
        FinalResponse <- Prompt_LLM_For_Response(ActionResults)
        
        Save_To_Memory(IncomingEvent, FinalResponse)
        
        RETURN FinalResponse

    END PROCEDURE

# Instructions and Necessities

## Necessities
- IDE with python (preferably **VS Code**)
- **Ollama** and **Mistral**
- **Docker**

## Instructions
What to do to start working and pick up exactly where you left off:

- Open **Docker Desktop** (make sure it turns green)
- Activate your env: `source .venv/Scripts/activate`
- Wake up the AI: `docker start ollama-enterprise`

What to do to end your work session

- Deactivate you env: `deactivate`
