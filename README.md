# Shopee AI Engineer Technical Test

Answers to the Shopee AI Engineer technical test: five written questions on AI agent
engineering (`docs/`) and five coding exercises (`src/`), covering CSV parsing at scale,
a from-scratch vector database, and a full receipt-tracking application with a tool-calling
LLM agent, containerized and deployed via CI/CD.

## Repository structure

```
.
├── docs/                           # Part 1 -- Engineering Knowledge AI Agent Test
│   ├── q1.md                       # REST API vs. MCP in the context of AI
│   ├── q2.md                       # How REST API / MCP improve AI use cases
│   ├── q3.md                       # Ensuring an AI agent answers correctly
│   ├── q4.md                       # Docker / containerization in the context of AI
│   └── q5.md                       # Fine-tuning an LLM from raw data
├── src/                            # Part 2 -- Coding Test
│   ├── 1-csv-parsing/              # Q1 + Q2 + Q3: small vs. large CSV parsing
│   ├── 2-vector-db/                # Q4: vector DB + cosine similarity from scratch
│   └── 3-online-food-receipt/      # Q5: receipt upload, extraction, and Q&A agent
└── .github/workflows/               # CI/CD (build + push the receipt app's Docker image)
```

## Part 1 -- Engineering Knowledge (`docs/`)

| # | Question | Answer |
|---|---|---|
| 1 | Differences between REST API and MCP in the context of AI | [docs/q1.md](docs/q1.md) |
| 2 | How REST API and MCP can improve AI use cases | [docs/q2.md](docs/q2.md) |
| 3 | How to ensure an AI agent answers correctly | [docs/q3.md](docs/q3.md) |
| 4 | What Docker/containerization enables in an AI context | [docs/q4.md](docs/q4.md) |
| 5 | How to fine-tune an LLM from raw data | [docs/q5.md](docs/q5.md) |

## Part 2 -- Coding Test (`src/`)

### 1. [CSV parsing](src/1-csv-parsing/) -- Q1, Q2, Q3

Parses `customer-100000.csv` and `customer-2000000.csv`, and demonstrates two different
strategies for the small vs. large file:

- **Small (100K rows)** -- loaded fully into memory with pandas, explored interactively in a
  notebook ([EDA insights](src/1-csv-parsing/README.md#key-insights-customer-100000csv)).
- **Large (2M rows)** -- streamed in 50,000-row chunks via `pandas`' `chunksize`, aggregating
  stats on the fly so peak memory stays flat (~30 MB) regardless of file size, measured with
  `tracemalloc`.

See [src/1-csv-parsing/README.md](src/1-csv-parsing/README.md) for the full write-up, including
why chunked streaming and full in-memory loading are different tools for different file sizes.

### 2. [Vector DB from scratch](src/2-vector-db/) -- Q4

A minimal vector database built with zero ML/vector dependencies -- in-memory storage with
JSON-file persistence, and a hand-written `cosine_similarity()` (no numpy/scipy/sklearn) for
search. Exposed as a FastAPI service and containerized with its own `Dockerfile`.

See [src/2-vector-db/README.md](src/2-vector-db/README.md) for the API, the math, and how to run
it with Docker.

### 3. [Online food receipt tracker](src/3-online-food-receipt/) -- Q5

A Streamlit app to upload photos of food receipts, extract structured data via an OpenAI vision
call, store it in Postgres, and ask natural-language questions about spending (e.g. *"What food
did I buy yesterday?"*, *"Give me total expenses for food on 20 June"*, *"Where did I buy
hamburger from in the last 7 days?"*) answered by a LangGraph tool-calling agent grounded in the
database rather than the LLM's own memory.

- Layered/DDD-style app (`domain` / `infrastructure` / `use_cases` / `agent`).
- Containerized with its own `Dockerfile` and `docker-compose.yml` (app + Postgres).
- CI/CD in [.github/workflows/online-food-receipt-ci.yaml](.github/workflows/online-food-receipt-ci.yaml)
  builds and pushes the Docker image on changes to this app.

See [src/3-online-food-receipt/README.md](src/3-online-food-receipt/README.md) for setup, the
project structure, and why the agent delegates arithmetic to SQL instead of doing it itself.

## Running each project

Each subproject under `src/` is self-contained with its own `pyproject.toml`, `uv.lock`, and
setup instructions -- see that project's README for exact steps. In general:

```bash
cd src/<project-dir>
uv sync
uv run <entrypoint>
```
