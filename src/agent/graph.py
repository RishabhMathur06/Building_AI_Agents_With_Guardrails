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

    # Call Gemini.
    response = call_gemini_with_tools(messages)

    # Check if gemini wants to call a tool. Depends on the repsonse strucutre of google-genai.
    tool_calls = []
    content = ""

    # Parse gemini response to see if it's a tool call or text.
    try:
        candidates = response.candidates[0]

        for part in candidates.content.parts:
            if part.function_call:
                # It's a tool call.
                fc = part.function_call
                tool_calls.append({
                    "name": fc.name,
                    "args": dict(fc.args)
                })
                print(f"--- DECISION: Agent wants to call tool: {fc.name}")

            if part.text:
                content += part.text

    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        content = "Error in agent reasoning."

    # Return the AI message, attached with tool calls metadata so, 
    # next node knows what to do.
    ai_msg = AIMessage(content=content, tool_calls=tool_calls if tool_calls else [])
    return {"messages": [ai_msg]}

def tool_executor_node(state: AgentState):
    """
    The 'Hands' node.
    Executes the tools requested by the agent.
    """
    print("--- 🛠️ TOOL NODE: Executing tools... ---")
    last_message = state['messages'][-1]

    tool_results = []

    # Iterate through all the requested tool calls.
    for tool_call in last_message.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        call_id = tool_call.get('id', 'simulated_id')   # langChain expects an ID

        result = "ERROR: Unknown tool"

        # Route to actual python functions defined in "tools.py".
        if tool_name == "query_10k_report":
            result = query_10K_report(tool_args.get('query'))
        elif tool_name == "get_real_time_market_data":
            result = get_real_time_market_data(tool_args.get('ticker'))
        elif tool_name == "execute_trade":
            result = execute_trade(
                tool_args.get('ticker'),
                int(tool_args.get('shares')),
                tool_args.get('order_type')
            )

        # Create a ToolMessage (standard Langchain format).
        tool_results.append(ToolMessage(
            tool_call_id=call_id,
            name=tool_name,
            content=str(result)
        ))

# --- Defining Conditional Logic ---
def should_continue(state: AgentState) -> Literal("tools", "__end__"):
    """
    Decides the path:
    - If LLM made tool calls -> Go to 'tools' node
    - If LLM just spoke text -> End the turn
    """
    last_message = state["messages"][-1]

    # Check if the message has tool calls attached.
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        print("--- DECISION: Agent has a final answer. Ending run. ---")
        return "__end__"

# --- Build the graph ---
workflow = StateGraph(AgentState)

# Add nodes.
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_executor_node)

# Set entry point.
workflow.set_entry_point("agent")

# Add edges.
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "__end__": END
    }
)

workflow.add_edge("tools", "agent")         # From 'tools', we always go back to 'agent' to let it digest the result.

# Compiling the graph.
unguarded_agent_app = workflow.compile()

print("✅ Unguarded agent graph compiled successfully.")