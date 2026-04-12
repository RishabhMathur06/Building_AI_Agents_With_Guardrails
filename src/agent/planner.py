"""
Agent Planner Module

Forces the agent to generate a structured action plan
before executing any tools.
"""

# Importing dependencies.
import json
from typing import Dict, Any, List

from langchain_core.messages import BaseMessage
from ..clients.gemini_client import gemini_client
from ..config import Config

# System prompt for planning.
PLANNING_SYSTEM_PROMPT = """
You are an autonomous financial assistant.

You have access to the following tools:
1. query_10K_report
2. get_real_time_market_data
3. execute_trade

Your task:
Create a step-by-step action plan to help the user.

IMPORTANT RULES:
- Only use the available tools
- If unsure, still propose a reasonable plan
- NEVER return an empty plan

Return ONLY JSON:
{
  "plan": [
    {
      "tool_name": "...",
      "arguments": {},
      "reasoning": "..."
    }
  ]
}
"""



def generate_action_plan(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a structured action plan from the user's prompt.

    Args:
        state: Agent state containing messages

    Returns:
        Dict containing action_plan
    """
    print("\n--- AGENT: Generating Action Plan ---")

    messages: List[BaseMessage] = state["messages"]
    last_message = messages[-1]

    prompt = last_message.content

    try:
        response = gemini_client.generate_json(
            prompt=prompt,
            system_instruction=PLANNING_SYSTEM_PROMPT,
            model=Config.MODEL_POWERFUL
        )

        print("\n🔍 RAW LLM RESPONSE:")
        print(response)

        # Handle multiple possible response formats
        if isinstance(response, dict) and "plan" in response:
            action_plan = response["plan"]
        elif isinstance(response, list):
            action_plan = response
        else:
            print("ERROR: Unexpected response format from LLM")
            print("Raw response:", response)
            action_plan = []

        # Clean invalid entries (very important)
        action_plan = [a for a in action_plan if isinstance(a, dict)]

        print("\nGenerated Action Plan:")
        print(json.dumps(action_plan, indent=4))

        return {"action_plan": action_plan}

    except Exception as e:
        print(f"ERROR generating action plan: {e}")

        return {"action_plan": []}
