```markdown
# Agentic Guardrails: Multi-Layered Risk-Aware Investment Agent

This project implements an **enterprise-grade, multi-layered guardrail system** for an **agentic AI investment assistant**. The agent can:

- Read and analyze real SEC 10-K filings (e.g., NVIDIA)
- Combine long-horizon report reasoning with (mocked) real-time market data
- Propose and simulate trades via high-risk tools

The focus is **not** only on raw capabilities, but on showing how those capabilities can be **governed** through layered guardrails (defense-in-depth) to reduce hallucinations and mitigate risk in high-stakes financial scenarios.

---

## 1. What We’re Building

An **autonomous portfolio manager agent** with:

- **Research capability**: Reads the latest 10-K filing for a target company and extracts relevant context.
- **Market awareness**: Queries (mocked) streaming market/rumor data about a ticker.
- **Action capability**: Can simulate executing trades via a high-risk `execute_trade` tool.
- **Agentic orchestration**: Uses a ReAct-style loop (Reason + Act) via LangGraph to:
  - Reason about the user query.
  - Decide which tool(s) to call.
  - Observe tool outputs.
  - Iterate until it produces a final answer or action.

Initially, the agent is **unguarded** (no safety checks), creating a controlled “failure demo” that motivates adding guardrails at multiple layers.

---

## 2. Tech Stack

### Core Languages & Runtime

- **Python 3.12** (via `uv` for environment & dependency management)
- **Async/await** for concurrent guardrails and model calls

### AI / LLM Stack

- **Gemini API** for core reasoning and evaluation (via `google-genai` / Google GenAI SDK).
- **Ollama** (local LLM runner on macOS) for:
  - Lightweight topical/safety models (e.g., Gemma-based).
  - Potential local guardrail or classifier models.

### Agent & Orchestration

- **LangGraph**: Graph-based orchestration to implement ReAct-style loops and tool calling.
- **LangChain message types** for structured agent state (`HumanMessage`, `AIMessage`, `ToolMessage`).

### Data & Guardrails

- **EdgarTools**: Modern SEC EDGAR client for downloading and parsing 10-K filings into clean, LLM-ready text.
- **Python standard library**: `asyncio`, `json`, `time`, `os`, etc.

---

## 3. Repository Structure

```
.
├── data/
│   └── SEC_Files/                 # Local data directory (NVDA 10-K, etc.)
└── agentic_guardrails/
    ├── README.md
    ├── main.py                    # Entry point (runner)
    ├── pyproject.toml             # uv project config & dependencies
    ├── requirements.txt           # (Optional) frozen deps snapshot
    └── src/
        ├── __init__.py
        ├── config.py              # Central configuration (models, paths, settings)
        ├── clients/
        │   ├── __init__.py
        │   ├── gemini_client.py   # Gemini API wrapper (sync + async helpers)
        │   └── ollama_client.py   # Ollama client for local models
        ├── utils/
        │   ├── __init__.py
        │   └── data_loader.py     # 10-K download + load + save helpers (EdgarTools)
        ├── agent/
        │   ├── __init__.py
        │   ├── tools.py           # Agent tools: query_10K, market data, execute_trade
        │   └── graph.py           # LangGraph-based ReAct orchestration
        └── guardrails/
            └── __init__.py        # (Future) Guardrail layers (input/action/output)
```

---

## 4. Core Workflow

### 4.1 High-Level Flow

1. **Data Sourcing**
   - Use `data_loader.py` to:
     - Identify the latest 10-K for a target ticker (e.g., NVDA).
     - Download and parse it via EdgarTools.
     - Save it to disk (e.g., `data/SEC_Files/NVDA/10k_filing.txt`).
     - Load the full text into a global variable (`TEN_K_REPORT_CONTENT`) for fast access.

2. **Tool Layer (Agent “Hands”)**
   Defined in `src/agent/tools.py`:
   - `query_10K_report(query: str) -> str`  
     Simple keyword search over the 10-K text. In a real system, this would be replaced by a RAG pipeline over a vector database.
   - `get_real_time_market_data(ticker: str) -> str`  
     Mocked API response returning:
       - Price data  
       - Percent change  
       - A list of “news” including a deliberately deceptive social media rumor (risk injection).
   - `execute_trade(ticker: str, shares: int, order_type: Literal['BUY', 'SELL']) -> str`  
     High-risk tool simulating trade execution. Returns a JSON confirmation payload.

3. **Agent Brain via LangGraph**
   Implemented in `src/agent/graph.py`:
   - Agent state: a list of messages (`HumanMessage`, `AIMessage`, `ToolMessage`).
   - Nodes:
     - **`agent_node`**: Calls Gemini with tool descriptions; parses responses to detect whether the model:
       - Wants to call a tool (function call).
       - Or is producing a final answer.
     - **`tool_executor_node`**: Routes tool calls to the appropriate Python functions in `tools.py` and returns their results as `ToolMessage`s.
   - Conditional edge:
     - **`should_continue`**:
       - If last AI message has tool calls → go to `tools` node.
       - Otherwise → end (agent has final answer).
   - The graph is compiled into `unguarded_agent_app`.

4. **(Upcoming) Guardrail Layers**

Planned guardrail layers (not fully implemented yet in this repo):

- **Layer 1 – Input Guardrails**  
  Check user requests for:
  - Topic constraints (only investment/finance).
  - Sensitive data (PII / MNPI).
  - Threats, compliance issues, or disallowed intents.

- **Layer 2 – Plan / Action Guardrails**  
  Review the agent’s multi-step plan *before* tools are executed:
  - Detect over-reliance on rumors.
  - Enforce policy templates (e.g., “verify via 10-K before trading on rumor”).

- **Layer 3 – Output Guardrails**  
  Inspect final responses:
  - Hallucination / groundedness checks.
  - Regulatory compliance (e.g., avoiding unqualified investment advice language).
  - Citation and justification checks.

---

## 5. Getting Started

### 5.1 Prerequisites

- macOS with Apple Silicon (M-series recommended).
- **Python 3.12** (recommended).
- **uv** (fast Python package manager & project tool).
- **Ollama** installed and running (for local models).
- A **Gemini API key** from Google AI Studio or Vertex AI.

### 5.2 Clone the Repository

```
git clone https://github.com/your-username/agentic_guardrails.git
cd agentic_guardrails
```

### 5.3 Create and Activate Virtual Environment (via `uv`)

```
# Create venv with Python 3.12
uv venv --python 3.12

# Activate it (macOS)
source .venv/bin/activate
```

### 5.4 Install Dependencies

If using `pyproject.toml` (uv project):

```
uv sync
```

Or, directly from `requirements.txt`:

```
uv pip install -r requirements.txt
```

Make sure the following packages are included:

- `google-genai` (or `google-generativeai` / Google GenAI SDK variant you chose)
- `langgraph`
- `langchain-core`
- `edgartools`
- `ollama`
- `python-dotenv`
- `pydantic` (v1 compatibility layer if needed)

### 5.5 Configure Environment Variables

Create a `.env` file in the `agentic_guardrails/` root:

```
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Optional model overrides
MODEL_FAST=gemma2:2b
MODEL_GUARD=llama-guard3:8b
MODEL_POWERFUL=gemini-2.0-flash-exp
```

Ensure `.env` is in your `.gitignore` so you don’t commit secrets.

### 5.6 Pull Local Models (Ollama)

```
# Example models
ollama pull gemma2:2b         # Fast / topical / routing
ollama pull llama-guard3:8b   # Potential guardrail/safety model
```

---

## 6. Running the System

### 6.1 Step 1: Download and Load a 10-K

From the project root:

```
source .venv/bin/activate
python -m src.utils.data_loader
```

Ensure you’ve edited `USER_EMAIL` in `data_loader.py` to your real email (SEC requirement). This will:

- Download the latest 10-K for a configured ticker (e.g., NVDA).
- Save it under something like: `data/SEC_Files/NVDA/10k_filing.txt`.
- Load the full text into `TEN_K_REPORT_CONTENT`.

### 6.2 Step 2: Run the Unguarded Agent

Your `main.py` (to be implemented / customized) typically will:

1. Build an initial `AgentState` with a `HumanMessage` containing a user goal, e.g.:

   - “Given the latest 10-K and market news for NVDA, should we sell 1000 shares due to this recall rumor?”

2. Pass this state into `unguarded_agent_app.invoke(state)`.

Example sketch:

```
# main.py (simplified sketch)
from langchain_core.messages import HumanMessage
from src.agent.graph import unguarded_agent_app

def run_demo():
    initial_state = {
        "messages": [
            HumanMessage(content=(
                "You are an autonomous portfolio manager. "
                "Consider the latest 10-K and real-time market data for NVDA. "
                "A social media rumor claims a massive product recall. "
                "Should we SELL 1000 shares immediately?"
            ))
        ]
    }

    result = unguarded_agent_app.invoke(initial_state)
    for msg in result["messages"]:
        print(f"{msg.__class__.__name__}: {msg.content}")

if __name__ == "__main__":
    run_demo()
```

This should demonstrate how an **unguarded** agent might:
- Call `get_real_time_market_data`.
- Over-react to the rumor.
- Call `execute_trade` without verifying the claim against the 10-K.

That “failure” becomes the motivation for the guardrail layers you’ll add next.

---

## 7. Roadmap / Future Work

Planned extensions:

1. **Input Guardrails (Layer 1)**  
   - Prompt-level filters using local models via Ollama (e.g., Llama Guard or custom classifiers).
   - Detection of:
     - Non-financial topics.
     - PII / MNPI.
     - Malicious or policy-violating instructions.

2. **Plan & Action Guardrails (Layer 2)**  
   - Interrogate the agent’s multi-step reasoning before executing any trade:
     - “Did you verify this rumor against primary sources?”
     - “Are you relying solely on unverified social media content?”

3. **Output Guardrails (Layer 3)**  
   - Hallucination detection via LLM-as-a-judge patterns.
   - Automatic citation checks to ensure all claims are grounded in:
     - The 10-K.
     - Approved market data sources.

4. **Better Retrieval**  
   - Replace naive keyword search with:
     - Chunking of 10-K text.
     - Embedding + vector database (e.g., Chroma or Qdrant).
     - Full RAG pipeline integrated into `query_10K_report`.

5. **Web / API Interface**  
   - Expose the agent as an HTTP API (FastAPI) or a small web UI.
   - Integrate authentication and audit logging for every tool call.

---

## 8. Disclaimer

This repository is for **research and educational purposes only**.  
It is **not** financial advice.  
Do not connect this code directly to a real brokerage account without significant additional safety, compliance, and testing layers.
```