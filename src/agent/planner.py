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

Your FIRST task is to create a step-by-step action plan to address the user's request.

The plan MUST:
- Be a list of tool calls
- Include reasoning for each step
- NOT execute anything

Respond ONLY with valid JSON:

{
  "plan": [
    {
      "tool_name": "tool_name_here",
      "arguments": {"arg1": "value"},
      "reasoning": "why this step is needed"
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

        action_plan = response.get("plan", [])

        print("\nGenerated Action Plan:")
        print(json.dumps(action_plan, indent=4))

        return {"action_plan": action_plan}

    except Exception as e:
        print(f"ERROR generating action plan: {e}")

        return {"action_plan": []}
