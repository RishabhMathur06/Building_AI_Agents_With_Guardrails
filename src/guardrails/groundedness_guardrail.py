"""
Groundedness Guardrail

Ensures that the agent's action plan reasoning
is based on actual available context (no hallucinations).
"""
# Importing Dependencies.
from typing import List, Dict, Any
from ..clients.gemini_client import gemini_client
from ..config import Config

def is_response_grounded(response: str, context: str) -> Dict[str, Any]:
    """
    Uses LLM to check if response is grounded in context.
    """
    system_prompt = """
    You are a strict factuality judge.

    Your task is to determine whether the given RESPONSE is fully supported
    by the provided CONTEXT.

    Rules:
    - If the response contains claims not supported by context → NOT grounded
    - If everything is supported → grounded

    Return ONLY JSON:
    {
        "is_grounded": true/false,
        "reason": "short explanation"
    }
    """

    prompt = f"""
    CONTEXT:
    {context}

    RESPONSE:
    {response}
    """

    try:
        result = gemini_client.generate_json(
            prompt=prompt,
            system_instruction=system_prompt,
            model=Config.MODEL_POWERFUL
        )

        return result

    except Exception as e:
        print(f"ERROR in groundedness check: {e}")
        return {
            "is_grounded": False,
            "reason": "Error during groundedness evaluation"
        }

def check_plan_groundedness(action_plan: List[Dict[str, Any]], conversation_history: str) -> Dict[str, Any]:
    """
    Checks if action plan reasoning is grounded in conversation history.
    """
    print("\n--- GUARDRAIL (Action/Groundedness): Checking Plan ---")

    if not conversation_history:
        return {
            "is_grounded": True,
            "reason": "No context available for grounding check"
        }
    
    # Combine all reasoning
    reasoning_text = " ".join(
        action.get("reasoning", "") for action in action_plan
    )

    return is_response_grounded(
        response=reasoning_text,
        context=conversation_history
    )