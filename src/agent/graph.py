"""
Agent Graph Module
Defines the LangGraph workflow (the "brain") for the agent.
It orchestrates the interaction between the LLM and the tools.
"""

# Importing dependencies.
from email import message
from typing import List, TypedDict, Any, Literal, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

from ..clients.gemini_client import gemini_client
from ..config import Config

from .tools import query_10K_report, get_real_time_market_data, execute_trade

# --- Defining the agent state ---
# "AgentState": memory of the agent holding the conversation history.
class AgentState(TypedDict):
    # "messages": list of message objects (Human, AI, Tool)
    messages: Annotated[List[BaseMessage], add_messages]        # Appends new messages instead of overwriting it.

# --- Defining tool logic for the LLM ---
def call_gemini_with_tools(messages: List[BaseMessage]):
    """
    Helper function to call Gemini API with our defined tools.
    """
    tools_config = [
        {
            "function_declarations": [
                {
                    "name": "query_10K_report",
                    "description": "Queries the 10-K report for specific information.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "query": {"type": "STRING", "description": "The search query"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_real_time_market_data",
                    "description": "Gets the real-time market data for a given ticker.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "ticker": {"type": "STRING", "description": "The stock ticker symbol (e.g., 'NVDA')."},
                        },
                        "required": ["ticker"]
                    }
                },
                {
                    "name": "execute_trade",
                    "description": "Executes a trade order. HIGH RISK.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "ticker":{"type": "STRING", "description": "The stock sticker"},
                            "shares":{"type": "INTEGER", "description": "Number of shares"},
                            "order_type": {"type": "STRING", "enum": ["BUY", "SELL"], "description": "Order type"}
                        },
                        "required": ["ticker", "shares", "order_type"]
                    }
                }
            ]
        }
    ]

    last_msg = messages[-1]
    prompt_text = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)

    # Calling Gemini.
    # Note: We need to access the underlying genai "client" object for advanced tool use.
    response = gemini_client.client.models.generate_content(
        model=Config.MODEL_POWERFUL,
        contents=prompt_text,
        tools=tools_config
    )

    return response

# --- Defining Nodes ---
def agent_node(state: AgentState):
    """
    The 'Brain' Node.
    Invokes the LLM to decide the next action.
    """
    print("--- 🧠 AGENT NODE: Deciding next step... ---")
    messages = state['messages']

    response = call_gemini_with_tools(messages)