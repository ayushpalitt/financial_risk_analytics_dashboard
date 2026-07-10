# Deployment Guide

This project is prepared for a three-service deployment:

- Backend API: Render Docker web service
- Database: Neon PostgreSQL
- Frontend: Vercel Next.js app

Generated data, model artifacts, and raw Kaggle files are intentionally excluded from Git. After the managed database is created, load it from your local generated CSV artifacts.

## 1. Database on Neon

1. Create a Neon project.
2. Create or use the default PostgreSQL database.
3. Copy the pooled or direct connection string.
4. Keep the connection string private; it will be used as `DATABASE_URL`.

## 2. Backend on Render

1. Push the latest repository state to GitHub.
2. In Render, create a new Blueprint or Docker web service from the GitHub repository.
3. Render will read `render.yaml` and create `financial-risk-api`.
4. Set these environment variables on the Render web service:

```text
DATABASE_URL=<neon-postgres-connection-string>
CORS_ORIGINS=https://<vercel-project>.vercel.app,http://localhost:3000
OPENAI_API_KEY=<optional-openai-api-key>
OPENAI_MODEL=gpt-5.5
AI_REPORTS_ENABLED=true
```

5. Deploy the Render service.

The backend Docker image runs this command at startup:

```bash
python -m backend.app.db.bootstrap && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

The bootstrap creates the core tables and API views. It does not load the large dataset.

## 3. Load the Neon PostgreSQL Data

Run these commands locally from the repository root:

```powershell
$env:DATABASE_URL = "<neon-postgres-connection-string>"
python scripts/load_processed_to_postgres.py --replace --database-url $env:DATABASE_URL
python scripts/load_fraud_predictions_to_postgres.py --database-url $env:DATABASE_URL
```

Use a Neon connection string that allows local client connections.

## 4. Frontend on Vercel

1. In Vercel, import the same GitHub repository.
2. Set the Root Directory to `frontend`.
3. Keep Framework Preset as Next.js.
4. Add these environment variables:

```text
BACKEND_API_BASE_URL=https://<render-backend-service>.onrender.com
NEXT_PUBLIC_API_BASE_URL=https://<render-backend-service>.onrender.com
```

5. Deploy the Vercel project.
6. If Vercel gives a production URL different from the one in `render.yaml`, update `CORS_ORIGINS` in the Render service environment to include the final Vercel URL.

## 5. Smoke Checks

After both services are deployed and the database is loaded:

```text
https://<render-backend-service>.onrender.com/health
https://<render-backend-service>.onrender.com/dashboard/overview
https://<render-backend-service>.onrender.com/ml/model-performance
https://<vercel-project>.vercel.app/
https://<vercel-project>.vercel.app/transactions
https://<vercel-project>.vercel.app/fraud
https://<vercel-project>.vercel.app/customers
https://<vercel-project>.vercel.app/machine-learning
https://<vercel-project>.vercel.app/executive-report
```

## Optional CLI Deployment

The repository does not require CLIs to deploy, but if you have Vercel CLI installed and authenticated:

```powershell
cd frontend
vercel --prod
```
