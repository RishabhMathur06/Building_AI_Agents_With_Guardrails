"""
Hallucination Guardrail (Layer 3)

Generates synthetic evaluation examples and will later
be used for final response validation.
"""

# Importing dependencies.
import json
from typing import List, Dict, Any

from ..clients.gemini_client import gemini_client
from ..config import Config

def generate_hallucination_eval_set(context: str, num_examples: int = 2) -> List[Dict[str, Any]]:
    """
    Generates factual and hallucinated statements based on context.

    Args:
        context (str): Trusted data (tool output)
        num_examples (int): Number of examples

    Returns:
        List of examples
    """
    print("\n--- GUARDRAIL (Output/Hallucination): Generating evaluation set ---")

    prompt = f"""
    Based on the following context, generate {num_examples} examples.

    One should be:
    - Factually correct (is_hallucination: false)

    One should be:
    - Plausible but incorrect (is_hallucination: true)

    Context:
    {context}

    Return ONLY JSON:
    {{
        "examples": [
            {{
                "statement": "...",
                "is_hallucination": true/false
            }}
        ]
    }}
    """

    try:
        response = gemini_client.generate_json(
            prompt=prompt,
            model=Config.MODEL_POWERFUL
        )

        examples = response.get("examples", [])

        if not examples:
            print("⚠️ No examples generated.")
            return []

        print(f"Generated {len(examples)} evaluation examples.\n")

        return examples

    except Exception as e:
        print(f"ERROR in hallucination eval generation: {e}")
        return []

def is_response_grounded(response: str, context: str) -> Dict[str, Any]:
    """
    Uses LLM-as-a-Judge to verify if response is grounded in context.

    Args:
        response (str): Final agent response
        context (str): Trusted tool output / data

    Returns:
        Dict with groundedness verdict
    """
    print("\n--- GUARDRAIL (Output/Groundedness): Checking response ---")

    judge_prompt = f"""
    You are a strict fact-checker.

    TASK:
    Determine whether the response is FULLY supported by the context.

    RULES:
    - Only use the provided context
    - Do NOT use external knowledge
    - If ANY part of response is unsupported → mark as NOT grounded

    Context:
    {context}

    Response:
    {response}

    Return ONLY JSON:
    {{
        "is_grounded": true/false,
        "reason": "short explanation"
    }}
    """

    try:
        result = gemini_client.generate_json(
            prompt=judge_prompt,
            model=Config.MODEL_POWERFUL
        )

        if not isinstance(result, dict):
            print("⚠️ Invalid judge response format")
            return {"is_grounded": False, "reason": "Invalid response format"}

        return result

    except Exception as e:
        print(f"ERROR in groundedness check: {e}")
        return {"is_grounded": False, "reason": "Judge model failure"}

def check_finra_compliance(response: str) -> Dict[str, Any]:
    """
    Checks if the response complies with FINRA Rule 2210.

    Args:
        response (str): Final agent output

    Returns:
        Dict with compliance verdict
    """
    print("\n--- GUARDRAIL (Output/FINRA): Checking compliance ---")

    finra_prompt = f"""
    You are a financial compliance officer.

    TASK:
    Evaluate whether the response complies with FINRA Rule 2210.

    RULE:
    - Must be fair and balanced
    - Must NOT be misleading
    - Must NOT contain:
        - Promissory language ("guaranteed returns")
        - Exaggeration
        - Speculative claims

    Response:
    {response}

    Return ONLY JSON:
    {{
        "is_compliant": true/false,
        "reason": "short explanation"
    }}
    """

    try:
        result = gemini_client.generate_json(
            prompt=finra_prompt,
            model=Config.MODEL_POWERFUL
        )

        if not isinstance(result, dict):
            print("⚠️ Invalid FINRA response format")
            return {"is_compliant": False, "reason": "Invalid response format"}

        return result

    except Exception as e:
        print(f"ERROR in FINRA compliance check: {e}")
        return {"is_compliant": False, "reason": "Compliance check failed"}

def verify_citations(response: str, context: str) -> Dict[str, Any]:
    """
    Verifies that citations in response exist in context.

    Args:
        response (str): Final agent output
        context (str): Source data

    Returns:
        Dict with citation validity
    """
    print("\n--- GUARDRAIL (Output/Citation): Verifying citations ---")

    try:
        # Simple heuristic: check if any bracketed citation exists
        import re
        citations = re.findall(r'\[(.*?)\]', response)

        if not citations:
            return {"citations_valid": True, "reason": "No citations present"}

        invalid = []
        for cite in citations:
            if cite not in context:
                invalid.append(cite)

        if invalid:
            return {
                "citations_valid": False,
                "reason": f"Invalid citations: {invalid}"
            }

        return {"citations_valid": True, "reason": "All citations valid"}
        
    except Exception as e:
        print(f"ERROR in citation check: {e}")
        return {"citations_valid": False, "reason": "Citation check failed"}