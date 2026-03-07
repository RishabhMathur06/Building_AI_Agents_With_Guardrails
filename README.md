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

**The Goal:** Initially, the agent is **unguarded**, creating a controlled environment to demonstrate failures (e.g., trading on rumors without verification). The ultimate objective is to implement **Input, Action, and Output Guardrails** to mitigate hallucinations and ensure regulatory compliance.

---

## ✨ Key Features

- **Research Capability**: Downloads and extracts relevant context from the latest 10-K filings.
- **Agentic Orchestration**: Uses **LangGraph** for a ReAct-style loop (Reason + Act) to decide on tool usage.
- **Tooling Layer**:
  - `query_10K_report`: Search SEC filings.
  - `get_real_time_market_data`: Access simulated market feeds.
  - `execute_trade`: Simulate trade execution.
- **Defense-in-Depth**: A structured approach to adding safety layers (Input, Plan, Output) around the LLM.

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
        │   └── graph.py           # LangGraph orchestration logic
        └── guardrails/
            └── __init__.py        # (Upcoming) Guardrail implementations
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

3.  **Agent Brain (`src/agent/graph.py`)**
    - **Agent Node**: Calls Gemini to determine the next step (tool call or final answer).
    - **Tool Node**: Executes the requested tool and returns output.
    - **Loop**: Continues until the agent generates a final response.

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

### 2. Run the Unguarded Agent

Execute the main script to see the agent in action:

```bash
python main.py
```

_Modify `main.py` to change the initial `HumanMessage` and test different scenarios._

**Example Scenario**:

> "Given the latest 10-K and market news for NVDA, a rumor claims a massive product recall. Should we SELL 1000 shares immediately?"

The unguarded agent may likely react to the rumor and attempt a trade without verification, demonstrating the need for the guardrails you will implement.

---

## 🛣 Roadmap

- [ ] **Layer 1: Input Guardrails**
  - Filter non-financial topics and PII.
  - Prevent malicious instructions using Llama Guard.
- [ ] **Layer 2: Plan & Action Guardrails**
  - Review agent plans before execution.
  - Enforce "verify before trading" policies.
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
