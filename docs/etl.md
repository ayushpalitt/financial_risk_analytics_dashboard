# ETL Pipeline

The ETL module converts the immutable Kaggle fraud dataset from `data/raw/creditcard.csv` into an enriched, analytics-ready transaction table at `data/processed/transactions_enriched.csv`.

## Responsibilities

- Load the raw CSV from `data/raw/creditcard.csv`.
- Validate the expected schema: `Time`, `V1` through `V28`, `Amount`, and `Class`.
- Check missing values and exact duplicate rows.
- Drop rows with missing required values.
- Drop exact duplicate raw transactions, keeping the first occurrence.
- Generate deterministic business fields using the configured random seed.
- Write an enriched processed CSV.
- Write a JSON quality report for audit and observability.

## Generated Business Columns

- `transaction_id`
- `customer_id`
- `merchant_id`
- `merchant_name`
- `merchant_category`
- `transaction_channel`
- `card_type`
- `city`
- `state`
- `customer_segment`
- `risk_score`
- `approval_status`
- `transaction_date`

The enrichment uses `RISK_ANALYTICS_RANDOM_SEED` from the environment, defaulting to `42`. Running the ETL repeatedly with the same raw file and seed produces the same processed dataset hash.

## Outputs

```text
data/processed/transactions_enriched.csv
data/processed/etl_quality_report.json
```

The processed CSV is intentionally ignored by Git because it is a generated data artifact. The raw dataset remains unchanged in `data/raw/creditcard.csv`.

## Run

```bash
python -m etl
```

Equivalent script entry point:

```bash
python scripts/run_etl.py
```

Custom paths and seed:

```bash
python -m etl \
  --raw-path data/raw/creditcard.csv \
  --processed-path data/processed/transactions_enriched.csv \
  --report-path data/processed/etl_quality_report.json \
  --seed 42
```

## Validate

```bash
python -m compileall etl scripts tests
python -m unittest discover -s tests
```
