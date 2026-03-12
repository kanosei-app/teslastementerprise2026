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
class CEOAgent(BaseAgent):
    def initializeAgent (self):
        self.memory = AgentMemory()
        self.tools = CEOToolkit()  (From notion this is analyitics dashboard and email notifiers)
        self.system_prompt = "You are the CEO. Your goal is to analyze inputs, delegate tasks, monitor KPIs, and summarize outcomes."

    def execute_reasoning_loop(self, incoming_event):
        
        1. RECEIVE (get user input + context)
        current_context = self.memory.get_recent_history()
        company_state = self.tools.get_dashboard_kpis()
        
        prompt_input = self._format_input(incoming_event, current_context, company_state)

        2. REASON (read system prompt, reason, get redy to output)

        reasoning_response = llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt_input,
            output_format="JSON" 
        )
        
        parsed_plan = self._parse_llm_response(reasoning_response)
        self.memory.save_thought(parsed_plan.thought)
       
       3. CALL TOOLS
        action_results = []
        
        for action in parsed_plan.actions:
            if action.name == "delegate_task":
                # Route to specific agent (e.g., Product, HR, Sales)
                result = self.tools.route_to_agent(
                    target=action.parameters['department'],
                    task=action.parameters['directive']
                )
                action_results.append(result)
                
            elif action.name == "replan_budget":
                # Trigger re-planning loop
                result = self.tools.adjust_financial_parameters(action.parameters)
                action_results.append(result)
                
            elif action.name == "summarize_cycle":
                # Finance reported ROI -> CEO summarizes outcomes
                result = self.tools.generate_executive_report(action.parameters)
                action_results.append(result)

        # If tools yield new critical info, the CEO might need to reason again (Recursive Loop)
        if self._requires_further_reasoning(action_results):
            return self.execute_reasoning_loop(action_results)

        # 4. RESPOND (aka output)

        # Update the Daily Dashboard Web UI
        self.tools.update_dashboard_logs(
            status="Idle", 
            latest_thought=parsed_plan.thought
        )
        
        # Format the final response to the user or system
        final_response = llm.generate(
            prompt=f"Based on these actions {action_results}, formulate a brief CEO update."
        )
        
        self.memory.save_interaction(incoming_event, final_response)
        
        return final_response
