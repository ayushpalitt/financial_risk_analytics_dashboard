# Database And SQL Analytics

The database module normalizes the enriched ETL output into PostgreSQL tables and exposes reusable SQL views for dashboard, machine learning, and executive-reporting workflows.

## Core Tables

- `customers`: customer segment, card type, and location dimensions.
- `merchants`: merchant names and merchant categories.
- `transactions`: transaction facts, fraud labels, risk scores, PCA feature columns, and generated fraud loss.
- `fraud_predictions`: model inference results keyed by transaction and model version.
- `daily_metrics`: refreshed daily dashboard metrics.

## Schema

Schema SQL is stored in:

```text
database/schema/001_create_core_schema.sql
database/migrations/001_create_core_schema.sql
```

The schema includes:

- Primary keys for all core entities.
- Foreign keys from transactions to customers and merchants.
- Foreign keys from fraud predictions to transactions.
- Check constraints for IDs, class labels, fraud alignment, amounts, risk scores, channels, approval states, and category values.
- Indexes for transaction date, customer history, merchant history, fraud filtering, risk sorting, and model version lookups.
- `refresh_daily_metrics()` for rebuilding the `daily_metrics` table from transaction facts.

## Analytics SQL

Analytics scripts live in `database/sql/`:

- `010_analytics_views.sql`: dashboard and BI views.
- `020_materialized_views.sql`: heavier aggregate materialized views.
- `030_refresh_analytics.sql`: refresh routine for daily metrics and materialized views.

Included analytics:

- Dashboard KPI overview.
- Daily revenue trend and running revenue.
- Daily fraud trend and rolling fraud rate.
- Monthly revenue and revenue ranking.
- Top customers and top merchants.
- Customer running totals.
- Merchant fraud trends.
- Fraud distribution and transaction histogram.
- Customer segment and merchant category summaries.
- Fraud heatmap by day, hour, and state.
- Model performance by model version.

## Load Processed Data

Run the ETL first:

```bash
python -m etl
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

The project maps Postgres to host port `55432` by default to avoid conflicts with local Postgres installations that commonly use `5432`.

Load the processed dataset, apply schema, refresh daily metrics, and apply analytics SQL:

```bash
python scripts/load_processed_to_postgres.py --replace
```

The loader reads:

```text
data/processed/transactions_enriched.csv
```

It upserts:

- `customers`
- `merchants`
- `transactions`

Then it refreshes:

- `daily_metrics`
- all materialized analytics views

## Load Fraud Predictions

After model training, load prediction rows into `fraud_predictions`:

```bash
python -m ml
python scripts/load_fraud_predictions_to_postgres.py
```

Model performance can then be queried from:

```sql
SELECT * FROM vw_model_performance_by_version;
```

This view evaluates the full scored portfolio after inference. The holdout test metrics used for model selection are stored in `ml/reports/model_performance.json`.

## Useful Queries

Dashboard overview:

```sql
SELECT * FROM vw_dashboard_overview;
```

Top customers:

```sql
SELECT *
FROM vw_top_customers
ORDER BY spend_rank
LIMIT 25;
```

Rolling fraud rate:

```sql
SELECT *
FROM mv_rolling_fraud_rate
ORDER BY metric_date;
```

High-risk transactions:

```sql
SELECT *
FROM vw_high_risk_transactions
ORDER BY risk_rank
LIMIT 100;
```

Refresh analytics after new loads:

```sql
SELECT refresh_daily_metrics();
REFRESH MATERIALIZED VIEW mv_daily_metrics;
REFRESH MATERIALIZED VIEW mv_monthly_revenue;
REFRESH MATERIALIZED VIEW mv_rolling_fraud_rate;
REFRESH MATERIALIZED VIEW mv_top_customers_90d;
REFRESH MATERIALIZED VIEW mv_top_merchants_90d;
REFRESH MATERIALIZED VIEW mv_customer_lifetime_value;
REFRESH MATERIALIZED VIEW mv_merchant_risk_summary;
REFRESH MATERIALIZED VIEW mv_hourly_fraud_trend;
```
