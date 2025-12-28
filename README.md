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
├── agent/               # AI agent module
│   ├── agent.py         # OpenAI agent logic & conversation handling
│   ├── tools.py         # Tool definitions for the AI agent
│   └── system_prompt.md # Agent system prompt
├── db/                  # Database layer
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
2. Seed DB: `uv uv run python -c "from db.connection import init_db; init_db(seed=True)"`
3. Run app: `uv run chainlit run main.py`
