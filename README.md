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
