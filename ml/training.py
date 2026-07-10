"""Train and persist fraud detection models."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.config import MLConfig
from ml.data import ModelingDataset, load_modeling_dataset
from ml.evaluation import choose_best_model, evaluate_binary_classifier


@dataclass(frozen=True)
class TrainingResult:
    """Outcome returned after a complete model training run."""

    best_model_name: str
    model_path: Path
    metrics_path: Path
    predictions_path: Path
    metrics: dict[str, Any]
    rows_scored: int


def train_fraud_models(config: MLConfig | None = None) -> TrainingResult:
    """Train candidate fraud models and persist the best performer."""

    active_config = config or MLConfig()
    dataset = load_modeling_dataset(active_config.processed_data_path)
    split_data = build_train_test_split(dataset, active_config)
    candidate_models = build_candidate_models(active_config)

    trained_models: dict[str, Any] = {}
    metrics_by_model: dict[str, dict[str, Any]] = {}

    for model_name, model in candidate_models.items():
        model.fit(split_data["x_train"], split_data["y_train"])
        fraud_probabilities = model.predict_proba(split_data["x_test"])[:, 1]
        trained_models[model_name] = model
        metrics_by_model[model_name] = evaluate_binary_classifier(
            y_true=split_data["y_test"],
            fraud_probabilities=fraud_probabilities,
            decision_threshold=active_config.decision_threshold,
        )

    best_model_name = choose_best_model(metrics_by_model)
    best_model = trained_models[best_model_name]
    prediction_export = build_prediction_export(dataset, best_model, active_config)

    metrics_report = build_metrics_report(
        config=active_config,
        dataset=dataset,
        split_data=split_data,
        metrics_by_model=metrics_by_model,
        best_model_name=best_model_name,
    )

    artifact = {
        "model": best_model,
        "metadata": {
            "model_name": active_config.model_name,
            "model_version": active_config.model_version,
            "selected_model": best_model_name,
            "feature_columns": list(dataset.feature_columns),
            "target_column": "Class",
            "decision_threshold": active_config.decision_threshold,
            "random_seed": active_config.random_seed,
            "selection_strategy": "max f1_score, then recall, then roc_auc",
            "metrics": metrics_by_model[best_model_name],
        },
    }

    active_config.model_path.parent.mkdir(parents=True, exist_ok=True)
    active_config.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    active_config.predictions_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(artifact, active_config.model_path)
    active_config.metrics_path.write_text(
        json.dumps(metrics_report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    prediction_export.to_csv(active_config.predictions_path, index=False)

    return TrainingResult(
        best_model_name=best_model_name,
        model_path=active_config.model_path,
        metrics_path=active_config.metrics_path,
        predictions_path=active_config.predictions_path,
        metrics=metrics_report,
        rows_scored=int(len(prediction_export)),
    )


def build_train_test_split(
    dataset: ModelingDataset,
    config: MLConfig,
) -> dict[str, Any]:
    """Create a deterministic stratified train/test split."""

    x_train, x_test, y_train, y_test, ids_train, ids_test = train_test_split(
        dataset.features,
        dataset.target,
        dataset.transaction_ids,
        test_size=config.test_size,
        random_state=config.random_seed,
        stratify=dataset.target,
    )

    return {
        "x_train": x_train,
        "x_test": x_test,
        "y_train": y_train,
        "y_test": y_test,
        "ids_train": ids_train,
        "ids_test": ids_test,
    }


def build_candidate_models(config: MLConfig) -> dict[str, Any]:
    """Create deterministic candidate models for fraud detection."""

    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=1_000,
                        random_state=config.random_seed,
                        solver="lbfgs",
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=config.random_forest_estimators,
            max_depth=config.random_forest_max_depth,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=config.random_seed,
            n_jobs=-1,
        ),
    }


def build_prediction_export(
    dataset: ModelingDataset,
    model,
    config: MLConfig,
) -> pd.DataFrame:
    """Score all processed transactions with the selected model."""

    fraud_probabilities = model.predict_proba(dataset.features)[:, 1]
    predicted_class = (fraud_probabilities >= config.decision_threshold).astype(int)
    return pd.DataFrame(
        {
            "transaction_id": dataset.transaction_ids,
            "model_name": config.model_name,
            "model_version": config.model_version,
            "fraud_probability": fraud_probabilities.round(6),
            "predicted_class": predicted_class,
            "prediction_threshold": config.decision_threshold,
        }
    )


def build_metrics_report(
    config: MLConfig,
    dataset: ModelingDataset,
    split_data: dict[str, Any],
    metrics_by_model: dict[str, dict[str, Any]],
    best_model_name: str,
) -> dict[str, Any]:
    """Build a JSON-serializable model performance report."""

    train_distribution = split_data["y_train"].value_counts().sort_index().to_dict()
    test_distribution = split_data["y_test"].value_counts().sort_index().to_dict()
    full_distribution = dataset.target.value_counts().sort_index().to_dict()

    return {
        "model_name": config.model_name,
        "model_version": config.model_version,
        "selected_model": best_model_name,
        "selection_strategy": "max f1_score, then recall, then roc_auc",
        "random_seed": config.random_seed,
        "decision_threshold": config.decision_threshold,
        "test_size": config.test_size,
        "feature_columns": list(dataset.feature_columns),
        "excluded_columns": [
            "risk_score",
            "approval_status",
            "is_fraud",
            "merchant_id",
            "customer_id",
        ],
        "row_counts": {
            "total": int(len(dataset.target)),
            "train": int(len(split_data["y_train"])),
            "test": int(len(split_data["y_test"])),
        },
        "class_distribution": {
            "total": {str(key): int(value) for key, value in full_distribution.items()},
            "train": {str(key): int(value) for key, value in train_distribution.items()},
            "test": {str(key): int(value) for key, value in test_distribution.items()},
        },
        "models": metrics_by_model,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train fraud detection models for the risk analytics platform."
    )
    parser.add_argument(
        "--processed-path",
        type=Path,
        default=MLConfig.processed_data_path,
        help="Path to data/processed/transactions_enriched.csv.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=MLConfig.model_path,
        help="Path where the best model artifact will be saved.",
    )
    parser.add_argument(
        "--metrics-path",
        type=Path,
        default=MLConfig.metrics_path,
        help="Path where model metrics JSON will be saved.",
    )
    parser.add_argument(
        "--predictions-path",
        type=Path,
        default=MLConfig.predictions_path,
        help="Path where prediction export CSV will be saved.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=MLConfig.random_seed,
        help="Fixed random seed used for train/test split and models.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = train_fraud_models(
        MLConfig(
            processed_data_path=args.processed_path,
            model_path=args.model_path,
            metrics_path=args.metrics_path,
            predictions_path=args.predictions_path,
            random_seed=args.seed,
        )
    )
    print(
        json.dumps(
            {
                "best_model_name": result.best_model_name,
                "model_path": str(result.model_path),
                "metrics_path": str(result.metrics_path),
                "predictions_path": str(result.predictions_path),
                "rows_scored": result.rows_scored,
                "best_model_metrics": result.metrics["models"][
                    result.best_model_name
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
