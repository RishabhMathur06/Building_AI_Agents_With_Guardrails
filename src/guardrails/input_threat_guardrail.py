"""
Input Guardrail: Threat & Compliance Detection

Uses a specialized safety model (Llama Guard 3) to detect:
- Malicious intent
- Policy violations
- Unsafe instructions
"""
# Importing dependencies.
import time
import re
from typing import Dict, Any

from ..clients.ollama_client import ollama_client
from ..config import Config

async def check_threats(prompt: str) -> Dict[str, Any]:
    """
    Uses Llama Guard model to check for threats and compliance violations.

    Args:
        prompt (str): User input prompt

    Returns:
        Dict[str, Any]:
            {
                "is_safe": bool,
                "policy_violations": List[str]
            }
    """
    print("--- GUARDRAIL (Input/Threat): Checking for threats with Llama Guard... ---")

    # Llama Guard Specific Format.
    conversation = (
        "<|begin_of_text|><|start_header_id|>user<|end_header|>\n\n"
        f"{prompt}<|eot_id|>"
    )

    start_time = time.time()

    try:
        response = await ollama_client.generate_async(
            model=Config.MODEL_GUARD,
            prompt=conversation,
            temperature=0.0,
            max_tokens=100
        )

        content = response.strip().lower()

        is_safe = "unsafe" not in content.lower()

        policy_violations = []

        if not is_safe:
            # Try extracting structured codes
            match = re.search(r'policy:\s*(.*)', content.lower())
            
            if match:
                policy_violations = [
                    code.strip() for code in match.group(1).split(',')
                ]
            else:
                # Fallback: infer violation type from text
                if "account" in prompt.lower():
                    policy_violations.append("PII_LEAK")
                if "sell" in prompt.lower():
                    policy_violations.append("FINANCIAL_RISK")
                if "rumor" in prompt.lower():
                    policy_violations.append("MISINFORMATION")

                
                # If nothing detected, still mark generic unsafe
                if not policy_violations:
                    policy_violations.append("UNSPECIFIED_UNSAFE")


        latency = time.time() - start_time

        print(
            f"--- GUARDRAIL (Input/Threat): "
            f"Safe: {is_safe}. "
            f"Violations: {policy_violations}. "
            f"Latency: {latency:.2f}s ---"
        )

        return {
            "is_safe": is_safe,
            "policy_violations": policy_violations
        }

    except Exception as e:
        print(f"--- GUARDRAIL (Input/Threat): ERROR - {e} ---")

        return {
            is_safe: "False",
            policy_violations: ["ERROR"]
        }