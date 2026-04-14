import asyncio
import json

from langchain_core.messages import HumanMessage

# Layer 1
from src.guardrails.input_guardrail_orchestrator import run_input_guardrails
from src.guardrails.input_guardrail_analyzer import analyze_input_guardrail_results

# Planner
from src.agent.planner import generate_action_plan

# Layer 2
from src.guardrails.layer2_orchestrator import aegis_layer2_orchestrator
from src.guardrails.dynamic_guardrails import validate_trade_action

# Layer 3
from src.guardrails.layer3_orchestrator import aegis_layer3_orchestrator

# Tools (mock or real)
from src.agent.tools import get_real_time_market_data
from src.utils.scorecard import generate_aegis_scorecard

# =========================
# MAIN PIPELINE
# =========================

async def run_agent():
    print("\n" + "="*60)
    print("AGENTIC GUARDRAILS SYSTEM - FULL EXECUTION")
    print("="*60 + "\n")

    # -------------------------
    # INPUT PROMPT
    # -------------------------
    user_prompt = """
    NVDA seems really volatile lately, I'm getting nervous.
    Maybe do something about my 200 shares?
    """

    state = {
        "messages": [HumanMessage(content=user_prompt)]
    }
    # =========================
    # STEP 1: INPUT GUARDRAILS
    # =========================
    print("\n=== STEP 1: INPUT GUARDRAILS (LAYER 1) ===")

    verdict = await analyze_input_guardrail_results(user_prompt)

    if not verdict["is_allowed"]:
        print("\n❌ BLOCKED AT LAYER 1")
        return

    sanitized_prompt = verdict["sanitized_prompt"]

    print("\n✅ INPUT PASSED")

    # =========================
    # STEP 2: ACTION PLAN
    # =========================
    print("\n=== STEP 2: ACTION PLAN GENERATION ===")

    state["messages"][-1] = HumanMessage(content=sanitized_prompt)

    plan_output = generate_action_plan(state)
    action_plan = plan_output.get("action_plan", [])

    if not action_plan:
        print("❌ No action plan generated")
        return

    state["action_plan"] = action_plan

    # =========================
    # STEP 3: LAYER 2
    # =========================
    print("\n=== STEP 3: ACTION GUARDRAILS (LAYER 2) ===")

    state = aegis_layer2_orchestrator(state, validate_trade_action)

    final_plan = state.get("action_plan", [])

    # Check if any action blocked
    blocked = any(a.get("verdict") == "BLOCKED" for a in final_plan)

    if blocked:
        print("\n❌ BLOCKED AT LAYER 2")
        print(json.dumps({"plan": final_plan}, indent=4))
        return

    print("\n✅ ACTION PLAN APPROVED")

    # =========================
    # STEP 4: TOOL EXECUTION (SIMPLIFIED)
    # =========================
    print("\n=== STEP 4: TOOL EXECUTION ===")

    # For now, simulate context
    context = get_real_time_market_data("NVDA")

    # =========================
    # STEP 5: RESPONSE GENERATION
    # =========================
    print("\n=== STEP 5: RESPONSE GENERATION ===")

    raw_response = f"""
    Based on current market data: {context}
    NVDA is experiencing volatility. Consider reviewing your position carefully.
    """

    print("\nRaw Response:")
    print(raw_response)

    # =========================
    # STEP 6: LAYER 3
    # =========================
    print("\n=== STEP 6: OUTPUT GUARDRAILS (LAYER 3) ===")

    layer3_result = aegis_layer3_orchestrator(
        response=raw_response,
        context=context
    )

    # =========================
    # FINAL OUTPUT
    # =========================
    print("\n" + "="*60)
    print("FINAL RESPONSE")
    print("="*60)

    print(layer3_result["sanitized_response"])

    print("\nSafety Status:", "✅ SAFE" if layer3_result["is_safe"] else "❌ SANITIZED")

    run_metrics = {
        "latency": input_results.get("overall_latency", "N/A"),

        "layer1": {
            "topic": input_results["topic_check"].get("topic"),
            "pii": "FAILED" if input_results["sensitive_data_check"].get("pii_found") else "PASSED",
            "threat": "FAILED" if not input_results["threat_check"].get("is_safe") else "PASSED",
        },

        "layer2": {
            "policy": "PASSED",  # you can refine later
            "hitl": "TRIGGERED" if any(
                a.get("verdict") == "BLOCKED" for a in state.get("action_plan", [])
            ) else "NOT TRIGGERED"
        },

        "layer3": {
            "groundedness": layer3_results["checks"]["groundedness"].get("is_grounded"),
            "compliance": layer3_results["checks"]["compliance"].get("is_compliant"),
        },

        "final_verdict": "REJECTED" if not layer3_results["is_safe"] else "APPROVED"
    }

    scorecard = generate_aegis_scorecard(run_metrics)

    print("\n================ AEGIS SCORECARD ================\n")
    print(scorecard)

# =========================
# RUN
# =========================

if __name__ == "__main__":
    asyncio.run(run_agent())
