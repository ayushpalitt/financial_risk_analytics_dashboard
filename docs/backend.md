# FastAPI Backend

The backend exposes database-backed JSON APIs for dashboard KPIs, revenue and fraud analytics, customers, transactions, machine learning performance, and executive reporting.

## Run Locally

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Run the API:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:

```text
http://localhost:8000/docs
```

Health check:

```text
GET /health
```

## Endpoints

- `GET /dashboard/overview`
- `GET /dashboard/revenue`
- `GET /dashboard/fraud`
- `GET /dashboard/customers`
- `GET /dashboard/transactions`
- `GET /ml/model-performance`
- `GET /ml/fraud-distribution`
- `POST /ai/report`
- `GET /ai/report`

## AI Executive Reports

`/ai/report` collects dashboard KPIs, fraud trend, customer and merchant analytics, and model performance. When `OPENAI_API_KEY` is configured, the backend uses the OpenAI Responses API. Without a key, it returns a deterministic Markdown report from the same dashboard inputs.

Environment:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
AI_REPORTS_ENABLED=true
```

## Docker

Build and run backend with Postgres:

```bash
docker compose up -d postgres backend
```

The backend container connects to Postgres using the internal Docker service hostname:

```text
postgres:5432
```

From the host machine, Postgres remains available at:

```text
127.0.0.1:55432
```

## Validate

```bash
python -m compileall backend etl ml scripts tests
python -m unittest discover -s tests
```
