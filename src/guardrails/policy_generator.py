"""
Policy Guardrail Generator

Uses LLM to convert natural language policies
into executable Python validation functions.
"""
# Importing Dependencies.
import re
from pathlib import Path
from typing import Optional

from ..clients.gemini_client import gemini_client
from ..config import Config

POLICY_FILE_PATH = Path("policy.txt")
DYNAMIC_GUARDRAIL_PATH = Path("src/guardrails/dynamic_guardrails.py")


def create_policy_file(policy_text: str):
    """
    Saves policy text to file.
    """
    POLICY_FILE_PATH.write_text(policy_text)
    print(f"Policy saved at: {POLICY_FILE_PATH}")

def generate_guardrail_code_from_policy(policy_content: str) -> str:
    """
    Uses Gemini to generate Python validation code.
    """
    print("\n--- GUARDRAIL GENERATOR AGENT: Generating Python Code ---")

    generation_prompt = f"""
    You are an expert Python developer specializing in financial compliance.

    Convert the following policies into a Python function:

    Function name: validate_trade_action

    Requirements:
    - Input: action: dict, market_data: dict
    - Output: dict with:
        {{
            "is_valid": bool,
            "reason": str
        }}

    Policies:
    {policy_content}

    ONLY return valid Python code.
    DO NOT include explanations.
    """

    try:
        response = gemini_client.generate(
            prompt=generation_prompt,
            model=Config.MODEL_POWERFUL,
            temperature=0.0
        )

        raw_output = response.strip()

        # Extract code block if present
        code_match = re.search(r"```python\n(.*?)```", raw_output, re.DOTALL)

        if code_match:
            code = code_match.group(1).strip()
        else:
            print("⚠️ No markdown block found, using raw output.")
            code = raw_output

        return code

    except Exception as e:
        print(f"ERROR generating guardrail code: {e}")
        return ""

def save_generated_guardrail(code: str):
    """
    Saves generated Python code to dynamic file.
    """
    DYNAMIC_GUARDRAIL_PATH.write_text(code)
    print(f"Generated guardrail saved at: {DYNAMIC_GUARDRAIL_PATH}")

def load_generated_guardrail():
    """
    Dynamically imports generated guardrail function.
    """
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_guardrails",
            DYNAMIC_GUARDRAIL_PATH
        )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module.validate_trade_action

    except Exception as e:
        print(f"ERROR loading generated guardrail: {e}")
        return None