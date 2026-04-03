"""
Input Guardrail: Topical Classification

This guardrail checks whether the user's request is related to
finance or investing. If the prompt is unrelated, it can be rejected
before invoking the expensive reasoning model.
"""

import json
import time
from typing import Dict, Any

from ..clients.ollama_client import ollama_client
from ..config import Config

async def check_topic(prompt: str) -> Dict[str, Any]:
    print("--- Guardrail (Input/Topic): Checking prompt topic ---")

    system_prompt = """
    You are a topic classifier.

    Classify the user's query into one of:
    - FINANCE_INVESTING
    - GENERAL_QUERY
    - OFF_TOPIC

    Respond ONLY in JSON format like:
    {"topic": "FINANCE_INVESTING"}
    """

    start_time = time.time()

    try:
        response = await ollama_client.generate_async(
            model=Config.MODEL_FAST,
            prompt=prompt,
            system=system_prompt,
            temperature=0.0
        )

        raw_output = response.strip()

        # --- Robust JSON extraction ---
        try:
            result = json.loads(raw_output)
        except:
            # fallback: try to extract manually
            if "finance" in raw_output.lower():
                result = {"topic": "FINANCE_INVESTING"}
            elif "general" in raw_output.lower():
                result = {"topic": "GENERAL_QUERY"}
            else:
                result = {"topic": "OFF_TOPIC"}

        latency = time.time() - start_time

        finance_keywords = [
            "stock", "shares", "nvda", "trading", "market", "sell", "buy"
        ]

        if any(word in prompt.lower() for word in finance_keywords):
            result["topic"] = "FINANCE_INVESTING"
            
        print(
            f"--- Guardrail (Input/Topic): "
            f"Topic: {result.get('topic')} | Latency: {latency:.2f}s ---"
        )

        return result

    except Exception as e:
        print(f"--- Guardrail (Input/Topic): ERROR - {e} ---")
        return {"topic": "ERROR"}
