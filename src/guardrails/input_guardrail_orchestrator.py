"""
Input Guardrail Orchestrator

Runs all Layer 1 guardrails in parallel using asyncio
to minimize latency.
"""
# Importing dependencies.
import asyncio
import time
from typing import Dict, Any

from .input_topic_guardrail import check_topic
from .input_sensitive_data_guardrail import scan_for_sensitive_data
from .input_threat_guardrail import check_threats

async def run_input_guardrails(prompt: str) -> Dict[str, Any]:
    """
    Executes all input guardrails concurrently.

    Guardrails:
    - Topic classification
    - Sensitive data detection (PII + MNPI)
    - Threat & compliance detection

    Args:
        prompt (str): User input

    Returns:
        Dict[str, Any]: Combined results from all guardrails
    """
    print("\n>>> EXECUTING AEGIS LAYER-1: INPUT GUARDRAILS (PARALLEL) <<<")

    start_time = time.time()

    # Create async tasks.
    topic_task = asyncio.create_task(check_topic(prompt))
    sensitive_task = asyncio.create_task(scan_for_sensitive_data(prompt))
    threat_task = asyncio.create_task(check_threats(prompt))

    # Wait for all tasks to complete.
    topic_result, sensitive_result, threat_result = await asyncio.gather(
        topic_task,
        sensitive_task,
        threat_task
    )

    total_latency = time.time() - start_time

    print(f">>> AEGIS LAYER-1 COMPLETE. Total latency: {total_latency:.2f}s <<<")

    # Combine results.
    final_results = {
        "topic_check": topic_result,
        "sensitive_data_check": sensitive_result,
        "threat_check": threat_result,
        "overall_latency": total_latency
    }

    return final_results