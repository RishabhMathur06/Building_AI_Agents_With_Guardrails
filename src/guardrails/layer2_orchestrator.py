"""
Aegis Layer 2 Orchestrator

Applies all action-level guardrails:
- Groundedness
- Policy Validation
- Human-in-the-loop
"""
# Importing dependencies.
import json
from typing import Dict, Any, List
from ..agent.tools import get_real_time_market_data
from .groundedness_guardrail import check_plan_groundedness
from .hitl_guardrail import human_in_the_loop_trigger

def aegis_layer2_orchestrator(state: Dict[str, Any], validate_trade_action) -> Dict[str, Any]:
    """
    Runs all Layer 2 guardrails on action plan.
    """
    print("\n>>> EXECUTING AEGIS LAYER 2: ACTION PLAN GUARDRAILS <<<")

    action_plan: List[Dict] = state.get("action_plan", [])
    messages = state.get("messages", [])

    # Build conversation history
    conversation_history = " ".join(
        msg.content for msg in messages
        if hasattr(msg, "content") and msg.content
    )

    # ----------------------------------------
    # Guardrail 5: Groundedness (Plan-level)
    # ----------------------------------------
    groundedness_result = check_plan_groundedness(
        action_plan,
        conversation_history
    )

    if not groundedness_result.get("is_grounded", False):
        print(
            f"\n--- 🛡️ GROUNDEDNESS FAILED ---\n"
            f"Reason: {groundedness_result.get('reason')}"
        )

        for action in action_plan:
            action["verdict"] = "BLOCKED"
            action["rejection_reason"] = "Plan not grounded in context"

        state["action_plan"] = action_plan
        return state

    print("--- ✅ GROUNDEDNESS PASSED ---")

    # ----------------------------------------
    # Per-action Guardrails
    # ----------------------------------------
    for i, action in enumerate(action_plan):
        tool_name = action.get("tool_name")
        action["verdict"] = "ALLOWED"  # default

        # Only apply deeper checks for high-risk tool
        if tool_name == "execute_trade":
            ticker = action.get("arguments", {}).get("ticker", "NVDA")
            market_data = json.loads(get_real_time_market_data(ticker))

            # ----------------------------------------
            # Guardrail 4: Policy Validation
            # ----------------------------------------
            validation_result = validate_trade_action(action, market_data)

            if not validation_result.get("is_valid", False):
                print(
                    f"\n--- 🛡️ POLICY FAILED ---\n"
                    f"Reason: {validation_result.get('reason')}"
                )

                action["verdict"] = "BLOCKED"
                action["rejection_reason"] = validation_result.get("reason")
                continue

            print("--- ✅ POLICY PASSED ---")

            # ----------------------------------------
            # Guardrail 6: Human-in-the-loop
            # ----------------------------------------
            if human_in_the_loop_trigger(action, market_data):
                approval = input(
                    "\n⚠️ ACTION REQUIRES APPROVAL → Execute trade? (yes/no): "
                ).lower()

                if approval != "yes":
                    print("--- ❌ HUMAN REVIEW: DENIED ---")
                    action["verdict"] = "BLOCKED"
                    action["rejection_reason"] = "Denied by human reviewer"
                else:
                    print("--- ✅ HUMAN REVIEW: APPROVED ---")

    state["action_plan"] = action_plan
    
    print("\n>>> AEGIS LAYER 2 COMPLETE <<<")

    return state