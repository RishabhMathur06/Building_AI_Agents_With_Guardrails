"""
Human-in-the-Loop (HITL) Guardrail

Triggers human approval for high-risk actions.
"""
# Importing dependencies.
from typing import Dict, Any

def human_in_the_loop_trigger(action: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
    """
    Determines whether an action requires human approval.

    Args:
        action: Action from action plan
        market_data: Current market data

    Returns:
        bool: True → requires human approval
    """
    tool_name = action.get("tool_name")
    args = action.get("arguments", {})

    # ----------------------------------------
    # Trigger 1: Any trade execution
    # ----------------------------------------
    if tool_name == "execute_trade":
        shares = args.get("shares", 0)
        price = market_data.get("price", 0)

        trade_value = shares * price

        # ----------------------------------------
        # Trigger 2: High-value trade
        # ----------------------------------------
        if trade_value > 5000:
            print(
                f"\n--- 🛡️ GUARDRAIL (HITL): TRIGGERED ---\n"
                f"Reason: High-value trade (${trade_value:,.2f})"
            )
            return True

    return False
