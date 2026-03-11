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
    """
    Uses a fast local model to classify the topic of the user prompt.

    Categories:
        - FINANCE_INVESTING
        - GENERAL_QUERY
        - OFF_TOPIC

    Args:
        prompt (str): User prompt

    Returns:
        Dict[str, Any]: {"topic": "<CATEGORY>"}
    """
    print("--- Guardrail (Input): Checking prompt topic ---")

    system_prompt = """
    You're a topic classifier.

    Classify the user's query into ONE of the following categories:
        - FINANCE_INVESTING
        - GENERAL_QUERY
        - OFF_TOPIC

    Respond ONLY with JSON:
    {"topic": CATEGORY}
    """

    start_time = time.time()

    try:
        response = await ollama_client.generate_async(
            model=Config.MODEL_FAST,
            prompt=prompt,
            system=system_prompt,
            temperature=0.0
        )

        result = json.loads(response)

        latency = time.time() - start_time

        print(
            f"--- Guardrail (Input): Topic is: '{result.get('topic', 'UNKNOWN')}'. Latency: {latency:.2f}s ---"
        )

        return result

    except Exception as e:
        print(f"--- Guardrail (Input): ERROR - {e} ---")

        return {"topic": "ERROR"}