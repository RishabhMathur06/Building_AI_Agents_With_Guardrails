# Agentic Guardrails: Multi-Layered Risk-Aware Investment Agent

A robust, enterprise-grade **autonomous portfolio manager agent** capable of reading SEC filings, analyzing market data, and simulating trades. This project focuses on demonstrating **multi-layered guardrails** (defense-in-depth) to govern AI agents in high-stakes financial environments.

---

## 📖 Table of Contents

- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Core Workflow](#-core-workflow)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#-usage)
- [Roadmap](#-roadmap)
- [Disclaimer](#-disclaimer)

---

## 💡 About The Project

This project builds an agent simulating a portfolio manager that can:

- **Read & Analyze**: Parse real SEC 10-K filings (e.g., NVIDIA) using `EdgarTools`.
- **Market Awareness**: Query (mocked) real-time market data and rumors.
- **Execute**: Propose and simulate trades via a high-risk `execute_trade` tool.

**The Goal:** The project demonstrates a transition from an **unguarded** agent (for demonstrating failures) to a heavily governed system. We are progressively implementing **Input, Action, and Output Guardrails** to mitigate hallucinations, block malicious inputs, and ensure regulatory compliance. **Layer 1 (Input Guardrails)** and **Layer 2 (Plan & Action Guardrails)** are now fully active!

---

## ✨ Key Features

- **Research Capability**: Downloads and extracts relevant context from the latest 10-K filings.
- **Agentic Orchestration**: Uses **LangGraph** for a ReAct-style loop (Reason + Act) to decide on tool usage.
- **Tooling Layer**:
  - `query_10K_report`: Search SEC filings.
  - `get_real_time_market_data`: Access simulated market feeds.
  - `execute_trade`: Simulate trade execution.
- **Defense-in-Depth**: A structured approach to adding safety layers (Input, Plan, Output) around the LLM.
  - **Layer 1 (Input Guardrails) [Active]**: Async, parallel execution of Topic Check, Threat Detection (Llama Guard), and Sensitive Data Scanning (PII/MNPI).
  - **Layer 2 (Plan & Action Guardrails) [Active]**: Plan generation using a designated planner, groundedness checking, dynamically generated policy validation, and Human-in-the-Loop (HITL) manual approval.

---

## 🛠 Tech Stack

### Languages & Runtime

- **Python 3.12**
- **uv** (for fast dependency management)
- **Async/await** architecture

### AI / LLM

- **Gemini API** (`google-genai`): Core reasoning engine.
- **Ollama**: Local model inference (e.g., Gemma 2, Llama Guard) for safety and routing.

### Frameworks & Libraries

- **LangGraph**: Graph-based agent orchestration.
- **LangChain**: Message primitives and tool handling.
- **EdgarTools**: SEC EDGAR client.
- **Pydantic**: Data validation.

---

## 📂 Project Structure

```bash
.
├── data/
│   └── SEC_Files/                 # Local storage for 10-K filings
└── agentic_guardrails/
    ├── README.md
    ├── main.py                    # Application entry point
    ├── pyproject.toml             # Project config & dependencies
    ├── requirements.txt           # Frozen dependencies
    └── src/
        ├── __init__.py
        ├── config.py              # Configuration settings
        ├── clients/
        │   ├── gemini_client.py   # Google Gemini API wrapper
        │   └── ollama_client.py   # Local Ollama client
        ├── utils/
        │   └── data_loader.py     # SEC data loading utilities
        ├── agent/
        │   ├── tools.py           # Agent tools (10K query, market data, trade)
        │   ├── planner.py         # Action plan generator
        │   └── graph.py           # LangGraph orchestration logic
        └── guardrails/
            ├── __init__.py
            ├── dynamic_guardrails.py            # Dynamically generated code from policies
            ├── groundedness_guardrail.py        # Checks plan against conversation history
            ├── hitl_guardrail.py                # Human-in-the-loop manual approval
            ├── input_guardrail_analyzer.py      # Layer 1 decision logic
            ├── input_guardrail_orchestrator.py  # Async parallel execution of guards
            ├── input_sensitive_data_guardrail.py# PII/MNPI detection & sanitization
            ├── input_threat_guardrail.py        # Llama Guard integration
            ├── input_topic_guardrail.py         # Finance/Investing context enforcement
            ├── layer2_orchestrator.py           # Applies all plan/action guardrails
            └── policy_generator.py              # LLM-based policy-to-code translator
```

---

## 🔄 Core Workflow

1.  **Data Sourcing**
    - The `data_loader.py` script identifies, downloads, and parses the latest 10-K filing for a target ticker.
    - Content is loaded into memory (`TEN_K_REPORT_CONTENT`) for quick access by the agent.

2.  **Tool Layer (`src/agent/tools.py`)**
    - **`query_10K_report`**: Keyword search over the filing text.
    - **`get_real_time_market_data`**: Returns mocked prices and risk-injected "rumors".
    - **`execute_trade`**: Simulates buying/selling stocks.

3.  **Aegis Layer 1: Input Guardrails**
    - Sanitizes the user prompt asynchronously (topic, threat, PII).

4.  **Planner (**`src/agent/planner.py`**)**
    - Generates a granular action plan based on the sanitized prompt.

5.  **Aegis Layer 2: Action Guardrails (`src/guardrails/layer2_orchestrator.py`)**
    - Validates groundedness.
    - Applies dynamic, AI-generated policy guardrails in real-time.
    - Triggers Human-in-the-Loop (HITL) for high-risk tool calls.

6.  **Agent Brain (`src/agent/graph.py`)**
    - Orchestrator that continues loop execution based only on approved steps.

---

## 🚀 Getting Started

### Prerequisites

- **OS**: macOS with Apple Silicon (recommended).
- **Python**: Version 3.12+.
- **Tools**: `uv` (package manager), `Ollama` (for local models).
- **API Keys**: Google Gemini API key.

### Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/agentic_guardrails.git
    cd agentic_guardrails
    ```

2.  **Set up Virtual Environment**

    ```bash
    uv venv --python 3.12
    source .venv/bin/activate
    ```

3.  **Install Dependencies**

    _Note for macOS users: `pygraphviz` require C-headers from the `graphviz` system package to build. Install `graphviz` first via Homebrew, then link the headers during `uv` installation:_

    ```bash
    brew install graphviz
    export CFLAGS="-I$(brew --prefix graphviz)/include"
    export LDFLAGS="-L$(brew --prefix graphviz)/lib"
    uv pip install pygraphviz

    # Then install the rest of the dependencies
    uv sync
    # OR
    uv pip install -r requirements.txt
    ```

### Configuration

Create a `.env` file in the `agentic_guardrails/` root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434

# Model Overrides (Optional)
MODEL_FAST=gemma2:2b
MODEL_GUARD=llama-guard3:8b
MODEL_POWERFUL=gemini-2.0-flash-exp
```

**Pull Local Models:**

```bash
ollama pull gemma2:2b
ollama pull llama-guard3:8b
```

---

## 💻 Usage

### 1. Download Investment Data

Initialize the system by downloading the necessary SEC filings:

```bash
source .venv/bin/activate
python -m src.utils.data_loader
```

_Note: Ensure `USER_EMAIL` is set in `data_loader.py` as per SEC requirements._

### 2. Run the Guarded Agent

Execute the main script to see the agent and its Layer 1 & 2 Guardrails in action:

```bash
uv run python main.py
```

_Modify `main.py` to change the predefined prompt and test different guardrail triggers._

**Example Layer 2 Scenario (HITL + Policy Validation)**:

> "NVDA seems really volatile lately, I'm getting nervous. Maybe do something about my 200 shares?"

This prompt passes the Layer 1 checks. The planner deduces a plan to check the market price and execute a sell order. The **Layer 2 Guardrails** then intercept:

- **Policy Validation Guardrail**: Validates the action plan against the generated trading parameters (e.g. avoiding panic selling when dropped above x%).
- **HITL Guardrail**: Pauses terminal execution to mandate human override (y/n) before actually proceeding to the `execute_trade` execution step!

---

## 🛣 Roadmap

- [x] **Layer 1: Input Guardrails**
  - Filter non-financial topics and PII/MNPI.
  - Prevent malicious instructions using Llama Guard.
- [x] **Layer 2: Plan & Action Guardrails**
  - Review agent plans before execution.
  - Enforce "verify before trading" policies.
  - Human-in-the-Loop review.
- [ ] **Layer 3: Output Guardrails**
  - Hallucination detection (LLM-as-a-judge).
  - Citation verification against source documents.
- [ ] **Enhanced Retrieval**
  - Implement RAG (Retrieval-Augmented Generation) with a vector database.
- [ ] **Web Interface**
  - Build a FastAPI backend and a simple UI for interaction.

---

## ⚠️ Disclaimer

This repository is for **research and educational purposes only**. It is **not** financial advice. Do not connect this code directly to a real brokerage account without significant additional safety, compliance, and testing layers.
