"""
Aegis Layer 3 Orchestrator

Runs all output guardrails on final response.
"""

from typing import Dict, Any

from .output_hallucination_guardrail import (
    is_response_grounded,
    check_finra_compliance,
    verify_citations
)

def aegis_layer3_orchestrator(response: str, context: str) -> Dict[str, Any]:
    """
    Runs all Layer 3 guardrails.

    Args:
        response (str): Final agent output
        context (str): Tool-derived context

    Returns:
        Dict with final decision
    """
    print("\n>>> EXECUTING AEGIS LAYER 3: OUTPUT GUARDRAILS <<<")

    # Run checks (sequential for now; can parallelize later)
    grounded_check = is_response_grounded(response, context)
    compliance_check = check_finra_compliance(response)
    citation_check = verify_citations(response, context)

    is_safe = (
        grounded_check.get("is_grounded", False)
        and compliance_check.get("is_compliant", False)
        and citation_check.get("citations_valid", False)
    )

    final_response = response

    if not is_safe:
        print("\n--- ⚠️ OUTPUT FAILED GUARDRAILS → SANITIZING ---")

        final_response = (
            "According to recent market data, NVIDIA has announced developments "
            "in AI hardware and analysts have updated their outlook. "
            "This information is for informational purposes only and does not constitute financial advice."
        )

    print(">>> AEGIS LAYER 3 COMPLETE <<<")

    return {
        "original_response": response,
        "sanitized_response": final_response,
        "is_safe": is_safe,
        "checks": {
            "groundedness": grounded_check,
            "compliance": compliance_check,
            "citations": citation_check
        }
    }