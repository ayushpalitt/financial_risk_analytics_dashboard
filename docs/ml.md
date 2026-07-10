# Machine Learning

The ML module trains fraud detection classifiers from the processed ETL dataset and exports both model artifacts and transaction-level fraud predictions.

## Models

Two supervised classifiers are trained:

- Logistic Regression with class balancing and feature scaling.
- Random Forest with balanced subsampling and deterministic random seed.

The best model is selected by:

1. F1 score
2. Recall
3. ROC AUC

This balances fraud detection precision and recall while still favoring useful probability ranking.

## Features

The model uses only source-safe transaction features:

- `Time`
- `Amount`
- `V1` through `V28`
- `amount_log`
- `hour_of_day`
- `is_night_transaction`

The model intentionally excludes generated business fields such as `risk_score`, `approval_status`, `is_fraud`, `customer_id`, and `merchant_id`. The ETL `risk_score` includes the known fraud label for business analytics enrichment, so using it as a training feature would leak the target.

## Outputs

```text
ml/models/fraud_model.pkl
ml/reports/model_performance.json
data/exports/fraud_predictions.csv
```

The saved model artifact contains:

- The trained sklearn pipeline or estimator.
- Model name and version.
- Selected model type.
- Feature list.
- Decision threshold.
- Evaluation metrics.

## Train

Run:

```bash
python -m ml
```

Equivalent script entry point:

```bash
python scripts/train_models.py
```

## Load Predictions Into PostgreSQL

Start PostgreSQL and load the processed transactions first:

```bash
docker compose up -d postgres
python scripts/load_processed_to_postgres.py --replace
```

Then load model predictions:

```bash
python scripts/load_fraud_predictions_to_postgres.py
```

The prediction loader upserts into `fraud_predictions` using the unique key:

```text
transaction_id, model_name, model_version
```

## Validate

```bash
python -m compileall etl ml scripts tests
python -m unittest discover -s tests
```
