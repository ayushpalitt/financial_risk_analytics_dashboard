# Next.js Dashboard

The frontend is a Next.js 15 enterprise dashboard for portfolio KPIs, transaction monitoring, fraud analytics, customer analytics, machine learning performance, and executive reporting.

## Stack

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Shadcn-style reusable UI components
- Recharts
- TanStack Table
- Framer Motion
- Lucide icons

## Run Locally

Start the backend first:

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open:

```text
http://127.0.0.1:3000
```

## Pages

- `/` - Dashboard overview
- `/transactions` - latest and high-risk transaction tables
- `/fraud` - fraud trends, distribution, and heatmap
- `/customers` - customer segments and top customers
- `/machine-learning` - model performance and confusion matrix
- `/executive-report` - AI/fallback executive Markdown report

## Environment

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001
BACKEND_API_BASE_URL=http://127.0.0.1:8001
```

## Validate

```bash
cd frontend
npm run type-check
npm run lint
npm run build
```

## Docker

The production image uses Next standalone output.

```bash
docker compose up -d frontend
```

The frontend container calls the backend through Docker networking:

```text
http://backend:8000
```
