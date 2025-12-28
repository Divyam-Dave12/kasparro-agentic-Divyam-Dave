# Agentic Content Automation System

A modular, multi-agent system designed to transform raw product data into structured, machine-readable content pages (FAQ, Product Listing, Comparison). 

Built for the **Kasparro Applied AI Challenge**.

---

## 🏗️ System Architecture

This project moves beyond simple "prompt engineering" to a robust **Agentic Graph**. It uses a sequential orchestrator pattern with strict schema enforcement at every step.



### Core Components

1.  **Orchestrator (`src/core/orchestrator.py`)**:
    * Manages the lifecycle of the request.
    * Implements a "Circuit Breaker" pattern (halts pipeline immediately on critical errors).
    * Passes a shared `WorkflowState` object between agents.

2.  **Shared State (`src/core/workflow_state.py`)**:
    * Source of Truth for the pipeline.
    * Stores Inputs (Raw Text, Structured Data).
    * Stores Artifacts (Questions, Competitor Data).
    * Stores Final Outputs (The 3 JSON pages).

### 🤖 The Agents

| Agent | Responsibility | Input | Output |
| :--- | :--- | :--- | :--- |
| **Data Ingestion** | Extract & Validate | Raw Text / JSON | Strict `ProductData` Schema |
| **Content Factory** | Generate & Assemble | `ProductData` | `faq.json`, `product_page.json`, `comparison_page.json` |

---

## 🚀 Key Features

* **Production-Ready Ingestion**: Handles both clean JSON and messy raw text (e.g., email copy-paste). Uses an LLM to extract structure before validation.
* **Strict Typing**: Uses `Pydantic` models to validate input data quality. The pipeline crashes early if data is invalid, rather than hallucinating.
* **JSON-First Design**: All agents communicate exclusively via Python Dictionaries/JSON. No markdown or free text is passed between internal logic blocks.
* **Decoupled Prompts**: All system prompts are externalized in `config/prompts.yaml`, allowing for iteration without code changes.

---

## 🛠️ Setup & Usage

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd kasparro-agentic-Divyam-Dave

# Install dependencies
pip install -r requirements.txt