# Online Food Receipt Tracker

A Streamlit app that lets a user upload photos of food purchase receipts, browse everything
they've uploaded, and ask natural-language questions about their spending -- powered by a
LangGraph tool-calling agent grounded in Postgres, not the LLM's memory.

- **Upload a receipt** -- a Gemini vision call extracts place, date, total, and line items;
  the user reviews/corrects the extraction before it's saved.
- **See all receipts** -- everything uploaded so far, with the original photo and items.
- **Ask about receipts** -- e.g. *"What food did I buy yesterday?"*, *"Give me total expenses
  for food on 20 June"*, *"Where did I buy hamburger from in the last 7 days?"*

## Project structure

Follows a lightweight layered/DDD style (domain / infrastructure / use_cases / agent), the
same conventions as the reference `app_v3` project, without the `modules/` split -- this app
has a single bounded context (receipts), so one flat layer set is enough.

```
app/
├── main.py                    # Streamlit entrypoint: page config + navigation
├── config.py                  # pydantic-settings (env-driven)
├── container.py                # dependency-injector wiring (composition root)
├── adapters.py                 # DB pool, Gemini chat model factory, local image storage
├── domain/
│   ├── entities.py             # Item, ParsedReceipt, Receipt
│   ├── repositories.py         # ReceiptRepository interface
│   └── exceptions.py
├── infrastructure/
│   └── db_repo.py               # PostgresReceiptRepository (psycopg, no ORM)
├── use_cases/
│   ├── parse_receipt.py         # ParseReceipt: image bytes -> ParsedReceipt (vision LLM)
│   ├── load_receipt.py          # LoadReceipt: persist image + parsed receipt
│   └── query_receipt.py         # List/Get/Search/SumExpenses + AskQuestion (agent-backed Q&A)
├── agent/                       # LangGraph Q&A agent
│   ├── state.py / context.py
│   ├── tools.py                  # search_food_receipts, sum_food_expenses
│   ├── graph.py                  # agent <-> tools ReAct loop
│   └── runner.py
└── entrypoints/pages/            # Streamlit pages (home, upload, data, agent)
```

### Why the agent doesn't do its own arithmetic

The agent has two tools: `search_food_receipts` (returns matching receipts as JSON) and
`sum_food_expenses` (returns an exact total computed in SQL). The system prompt explicitly
tells the model to always call `sum_food_expenses` for totals instead of adding numbers up
itself -- correctness for "how much did I spend" questions comes from grounding the number in
a deterministic database query, not from LLM math.

## Setup

Requires Python 3.11+, [uv](https://github.com/astral-sh/uv), and Docker (for local Postgres).

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Start Postgres:
   ```bash
   docker compose up -d
   ```
3. Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   ```
   LLM__GOOGLE_API_KEY=<your Google AI Studio API key>
   ```
   The database URL in `.env.example` already matches `docker-compose.yml`.

## Usage

```bash
uv run streamlit run main.py
```

Or with Docker:

```bash
docker compose up --build
```

The database schema (tables + indexes) is created automatically on first run. Uploaded
receipt photos are stored under `data/receipts/` (gitignored).
