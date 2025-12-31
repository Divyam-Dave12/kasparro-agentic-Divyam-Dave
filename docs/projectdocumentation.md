# Agentic Content Automation System

A modular, multi-agent system designed to transform raw product data into structured, machine-readable content pages (FAQ, Product Listing, Comparison).

Built for the **Kasparro Applied AI Challenge**.

---

## 🏗️ System Architecture: The "Supervisor-Worker" Model

Unlike traditional linear scripts, this project implements a **Dynamic Hub-and-Spoke Architecture**.

Instead of a hardcoded sequence (A → B → C), a central **Supervisor Agent** (The Brain) analyzes the current `WorkflowState` and dynamically decides which specialist agent to call next. This allows for **loops, retries, and self-correction**.



### 🔄 The Feedback Loop (Self-Correction)

The system includes a **Quality Assurance Cycle**:
1.  **Draft:** The system generates content.
2.  **Review:** A specialized `ReviewerAgent` critiques the output.
3.  **Refine:** If quality checks fail, the system automatically loops back to the `DraftingAgent` to fix errors before finishing.

---

### 🤖 The Agents

| Agent | Type | Responsibility |
| :--- | :--- | :--- |
| **Supervisor** | 🧠 Brain | Analyzes state, routes tasks, and halts on critical errors. |
| **Data Ingestion** | 🛠 Worker | Extracts strict JSON from messy raw text & validates schema. |
| **Researcher** | 🔎 Worker | Generates auxiliary data (Competitor Analysis, User Questions). |
| **Drafter** | ✍️ Worker | Assembles the final 3 JSON content pages. |
| **Reviewer** | ⚖️ QA | Validates final outputs. Triggers a **retry loop** if quality is low. |

---

## 🚀 Key Features

* **Dynamic Orchestration**: The sequence of execution is not hardcoded. The Supervisor decides the next step based on data availability.
* **Self-Healing Workflow**: If the Reviewer detects missing sections or empty answers, it rejects the state and forces a re-draft.
* **Production-Grade Robustness**:
    * **Circuit Breakers**: Stops infinite loops or critical API failures instantly.
    * **Strict Typing**: Uses `Pydantic` models to enforce data integrity at every step.
    * **Auto-Discovery Gateway**: The LLM service automatically detects available models (e.g., `gemini-1.5-flash` vs `gemini-pro`) to prevent 404 errors.
* **JSON-First Design**: All agents communicate exclusively via Python Dictionaries/JSON.

---

## 🛠️ Setup & Usage

### 1. Installation

```bash
# Clone the repository
git clone [https://github.com/Divyam-Dave12/kasparro-agentic-Divyam-Dave.git](https://github.com/Divyam-Dave12/kasparro-agentic-Divyam-Dave.git)
cd kasparro-agentic-Divyam-Dave

# Install dependencies
pip install -r requirements.txt

2. Configuration
Create a .env file in the root directory. You can use OpenAI OR Google Gemini (Free Tier):

Ini, TOML

# Option A: Google Gemini (Recommended for Free Testing)
GEMINI_API_KEY=AIzaSy...

# Option B: OpenAI
 OPENAI_API_KEY=sk-...
3. Running the System
To run the full autonomous pipeline:

Bash

python main.py
You will see the Supervisor dynamically routing tasks:

🚀 Orchestrator Started (Dynamic Mode)
👉 Supervisor chose: ingestor
👉 Supervisor chose: researcher
👉 Supervisor chose: drafter
👉 Supervisor chose: reviewer
✅ System Finished.

4. Running Tests
The project includes unit tests for individual agents and edge-case handling.

Bash

pytest tests/
📂 Project Structure
src/
├── agents/
│   ├── supervisor.py       # The Routing Logic (Brain)
│   ├── data_ingestion.py   # Raw Text -> Structured Data
│   ├── researcher.py       # Competitor & Question Generation
│   ├── drafter.py          # Final Page Assembly
│   └── reviewer.py         # Quality Assurance (Feedback Loop)
├── core/
│   ├── orchestrator.py     # Execution Loop
│   └── workflow_state.py   # Shared State Object
├── services/
│   └── llm_gateway.py      # Multi-Provider Wrapper (Gemini/OpenAI)
└── schemas/
    └── product_data.py     # Pydantic Validation Models