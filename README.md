# <img src="public/icon.png" height="41" align="center"> PharmaBot

PharmaBot is an AI-powered chatbot designed to assist users with information regarding medications, prescription management and stock management for a digital pharmacy.

## Tech Stack - Python

### Backend

- Vanila OpenAI API - using GPT-5
- Pydantic for tool definitions and data validation
- SQLite db for managing users, prescriptions and inventory data (Python standard library)

### Frontend

- [Chainlit](https://github.com/Chainlit/chainlit) for building the chatbot interface and managing user interactions

## Architecture

### Directory Structure

``` txt
pharmacist-assistant/
├── .chainlit/           # Chainlit config
├── agent/
│   ├── agent.py         # Agent logic & conversation handling
│   ├── tools.py         # Tool definitions
│   └── system_prompt.md
├── db/
│   ├── sql/             # Schema & seed data
│   ├── models/          # Pydantic models & dosage utilities
│   ├── repositories/    # Data access
│   └── connection.py    # SQLite connection management
├── public/              # Static assets
└── main.py              # Chainlit app entry point
```

### Database Tables

- **users** - Customer accounts (identified by 4-digit PIN)
- **medications** - Drug catalogue with bilingual names/descriptions
- **prescriptions** - Links users to medications with supply tracking
- **stock** - Inventory levels per medication/dosage combination
- **ingredients** - Active ingredients (many-to-many with medications)
- **dosage_instructions** - Dosing info, frequency, and warnings

### Tools

| Tool | Description |
|------|-------------|
| `get_dosage_instructions` | Get usage instructions (doses, frequency, warnings) |
| `get_medication_stock` | Get stock info for a medication (dosages, quantities) |
| `get_medications_by_ingredient` | Find medications containing an active ingredient |
| `load_prescriptions` | Load active prescriptions for a user by PIN |
| `reserve_medications` | Reserve medications (validates prescriptions, updates stock) |

### General Guidelines

- Verbose tool definitions and outputs - help dictate the flow without relying on the system prompt as much
- All validation happens in the backend - helps prevent prompt injection and jailbreak attacks

## Installation

> Clone the repo and navigate to the project directory.

Environment variables:

```dotenv
# OpenAI API key (required)
OPENAI_API_KEY=sk-***

# Model to use (optional, defaults to gpt-5)
# OPENAI_MODEL=gpt-5.2

# Reasoning effort for the model (optional, defaults to low)
# REASONING_EFFORT=medium
```

### Docker

1. Build: `docker build -t pharmabot .`
2. Run: `docker run -e OPENAI_API_KEY="sk-***" -p 8080:8080  pharmabot`
3. Open in browser: `http://localhost:8080`

> Can also run with a `.env` file: `docker run --env-file .env -p 8080:8080 pharmabot`

### UV

1. Install dependencies: `uv sync`
2. Seed DB: `uv run python -c "from db.connection import init_db; init_db(seed=True)"`
3. Run app: `uv run chainlit run main.py`

## Examples (Screenshots)

- [Dosage information](examples/dosage_info.png) - OTC dosage instructions for Advil
- [Alternative dosage](examples/alternative_dosage.png) - Prescription refill with alternative dosage reservation
- [OTC out of stock](examples/otc_out_of_stock.png) - Finding alternatives and reserving when medication is out of stock

## General Evaluation Guidelines

> Was used manually to test the chatbot during development

- [Plan](docs/evaluation.md) - Evaluation plan for testing policy compliance, tool accuracy, and bilingual behavior
- [Flows](docs/flows.md) - Multi-step conversation flows (stock check, prescription reservation, dosage info)
- [Scenarios](docs/scenarios.md) - Test scenarios for out-of-stock medications and prescription edge cases

## Future Plans

> (Some things I wanted to do if I had more time)

- Automated tests for functions and tools
- Automated LLM as a judge evaluation
- Latency optimizations - smaller models / reasoning effort `none` with gpt-5.2 etc...
