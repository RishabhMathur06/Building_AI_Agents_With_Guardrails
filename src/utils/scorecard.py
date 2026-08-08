"""
Aegis Scorecard Module

Generates a structured summary of guardrail performance
for each agent run.
"""

import pandas as pd
from typing import Dict, Any


def generate_aegis_scorecard(run_metrics: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate a scorecard summarizing all guardrail layers.

    Args:
        run_metrics: Dictionary containing results from all layers

    Returns:
        pandas DataFrame
    """

    layer1 = run_metrics.get("layer1", {})
    layer2 = run_metrics.get("layer2", {})
    layer3 = run_metrics.get("layer3", {})

    data = {
        "Metric": [
            "Overall Latency (s)",
            "Estimated Cost (USD)",

            "--- Layer 1: Input ---",
            "Topical Check",
            "PII Check",
            "Threat Check",

            "--- Layer 2: Action ---",
            "Policy Check",
            "Human-in-the-Loop",

            "--- Layer 3: Output ---",
            "Groundedness Check",
            "Compliance Check",

            "FINAL VERDICT"
        ],

        "Value": [
            run_metrics.get("latency", "N/A"),
            run_metrics.get("cost", "N/A"),

            "---",
            layer1.get("topic", "N/A"),
            layer1.get("pii", "N/A"),
            layer1.get("threat", "N/A"),

            "---",
            layer2.get("policy", "N/A"),
            layer2.get("hitl", "N/A"),

            "---",
            layer3.get("groundedness", "N/A"),
            layer3.get("compliance", "N/A"),

            run_metrics.get("final_verdict", "UNKNOWN")
        ]
    }

    df = pd.DataFrame(data).set_index("Metric")
    return df
