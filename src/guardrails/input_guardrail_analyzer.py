"""
Input Guardrail Analyzer

Applies decision logic on top of Layer 1 guardrail outputs.
Determines whether to:
- Allow prompt
- Reject prompt
- Use sanitized version
"""
# Importing dependencies.
from typing import Dict, Any

from .input_guardrail_orchestrator import run_input_guardrails

async def analyze_input_guardrail_results(prompt: str) -> Dict[str, Any]:
    """
    Runs input guardrails and applies decision logic.

    Args:
        prompt (str): User input

    Returns:
        Dict[str, Any]:
            {
                "is_allowed": bool,
                "reasons": List[str],
                "sanitized_prompt": str,
                "raw_results": Dict
            }
    """
    # Run Layer-1 guardrails.
    results = await run_input_guardrails(prompt)

    is_allowed = True
    rejection_reasons = []

    # --- Decision Logic ---
    # 1. Topic Check
    if results["topic_check"].get("topic") not in ["FINANCE_INVESTING"]:
        is_allowed = False
        rejection_reasons.append(
            f"Off-topic query (Topic: {results['topic_check'].get('topic')})"
        )

    # 2. Threat Check
    if not results["threat_check"].get("is_safe"):
        is_allowed = False
        rejection_reasons.append(
            f"Threat detected. Violation: {results['threat_check'].get('policy_violations')}"
        )

    # 3. Sensitive Data Check
    if(
        results["sensitive_data_check"].get("pii_found") or results["sensitive_data_check"].get("mnpi_risk")
    ):
        is_allowed = False
        rejection_reasons.append(
            "Sensitive data (PII or potential MNPI) detected in prompt."
        )

    # Extract sanitized prompt.
    sanitized_prompt = results["sensitive_data_check"].get("redacted_prompt")

    # --- Logging / Debugging Output ---
    print("\n------ AEGIS LAYER 1 ANALYSIS ------")

    if is_allowed:
        print("VERDICT: PROMPT ALLOWED. PROCEEDING TO AGENT CORE.")
        print(f"Sanitized Prompt: {sanitized_prompt}")
    else:
        print("VERDICT: PROMPT REJECTED. AGENT EXECUTION BLOCKED.")
        print("REASONS:")
        for reason in rejection_reasons:
            print(f"  - {reason}")

    print("\nThreat Analysis (Llama Guard):")
    print(f"  - Safe: {results['threat_check'].get('is_safe')}")
    print(f"  - Policy Violations: {results['threat_check'].get('policy_violations')}")

    print("\nSensitive Data Analysis:")
    print(f"  - PII Found: {results['sensitive_data_check'].get('pii_found')}")
    print(f"  - MNPI Risk: {results['sensitive_data_check'].get('mnpi_risk')}")
    print(f"  - Redacted Prompt: {sanitized_prompt}")

    print("\nTopical Analysis:")
    print(f"  - Topic: {results['topic_check'].get('topic')}")

    return {
        "is_allowed": is_allowed,
        "reasons": rejection_reasons,
        "sanitized_prompt": sanitized_prompt,
        "raw_results": results
    }