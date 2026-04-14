import asyncio

from src.guardrails.input_guardrail_orchestrator import run_input_guardrails

async def run_full_aegis_system(prompt: str):
    """Runs the full Aegis system (Layer 1 focus test)."""
    print("\n============================================================")
    print("🚀 RUNNING FULL AEGIS SYSTEM TEST")
    print("============================================================")

    # =========================
    # LAYER 1: INPUT GUARDRAILS
    # =========================
    results = await run_input_guardrails(prompt)

    threat_safe = results["threat_check"].get("is_safe", False)
    pii_found = results["sensitive_data_check"].get("pii_found", False)

    print("\n------ AEGIS LAYER 1 ANALYSIS ------")

    if not threat_safe or pii_found:
        print("VERDICT: ❌ PROMPT REJECTED")
        print("REASON: Threat or sensitive data detected")

        final_response = (
            "I am unable to process your request. "
            "The query was flagged for containing sensitive personal information "
            "and requesting a potentially non-compliant financial action.\n\n"
            "Please remove any account numbers and avoid acting on unverified rumors. "
            "I can assist with research and analysis instead."
        )

        print("\n------ FINAL SYSTEM RESPONSE ------")
        print(final_response)

        return {
            "status": "BLOCKED",
            "response": final_response
        }

    # =========================
    # PASSED LAYER 1
    # =========================
    print("VERDICT: ✅ PROMPT ALLOWED")
    print("Proceeding to Layer 2 (not executed in this test)")

    return {
        "status": "ALLOWED",
        "response": "Prompt passed Layer 1"
    }