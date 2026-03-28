"""
Input Guardrail: Sensitive Data Detection

This guardrail detects and redacts Personally Identifiable Information (PII)
and flags potential Material Non-Public Information (MNPI) risks.
"""

# Importing dependencies
import re
import time
from typing import Dict, Any

async def scan_for_sensitive_data(prompt: str) -> Dict[str, Any]:
    """
    Detects and redacts sensitive information in the prompt.

    Checks for:
    - Account numbers (PII)
    - Keywords indicating potential MNPI

    Args:
        prompt (str): User input prompt

    Returns:
        Dict[str, Any]:
            {
                "pii_found": bool,
                "mnpi_risk": bool,
                "redacted_prompt": str
            }
    """
    print("--- Guardrail (Input/SensitiveData): Scanning for sensitive data... ---")

    start_time = time.time()

    #Regex pattern to detect account numbers
    account_number_pattern = r'\b(ACCT|ACCOUNT)[- ]?(\d{3}[- ]?){2}\d{4}\b'

    # Redact detected account numbers
    redacted_prompt = re.sub(
        account_number_pattern,
        "[REDACTED_ACCOUNT_NUMBER]",
        prompt,
        flags=re.IGNORECASE
    )

    pii_found = redacted_prompt != prompt

    # Keywords that may indicate MNPI
    mnpi_keywords = [
        "insider_info",
        "upcoming merger",
        "unannounced earning",
        "confidential partnership"
    ]

    mnpi_risk = any(keyword in prompt.lower() for keyword in mnpi_keywords)

    latency = time.time() - start_time

    print(
        f"--- Guardrail (Input/SensitiveData): "
        f"PII found: {pii_found}, MNPI Risk: {mnpi_risk}. "
        f"Latency: {latency:.4f}s ---"
    )

    return {
        "pii_found": pii_found,
        "mnpi_risk": mnpi_risk,
        "redacted_prompt": redacted_prompt
    }