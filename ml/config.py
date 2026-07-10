"""Configuration for model training and prediction export."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANDOM_SEED = int(os.getenv("RISK_ANALYTICS_RANDOM_SEED", "42"))


@dataclass(frozen=True)
class MLConfig:
    """Runtime configuration for fraud model training."""

    processed_data_path: Path = (
        PROJECT_ROOT / "data" / "processed" / "transactions_enriched.csv"
    )
    model_path: Path = PROJECT_ROOT / "ml" / "models" / "fraud_model.pkl"
    metrics_path: Path = PROJECT_ROOT / "ml" / "reports" / "model_performance.json"
    predictions_path: Path = PROJECT_ROOT / "data" / "exports" / "fraud_predictions.csv"
    random_seed: int = DEFAULT_RANDOM_SEED
    test_size: float = 0.20
    decision_threshold: float = 0.50
    model_name: str = "fraud_detection_classifier"
    model_version: str = "1.0.0"
    random_forest_estimators: int = 120
    random_forest_max_depth: int = 14
