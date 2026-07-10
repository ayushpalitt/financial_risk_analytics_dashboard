"""Tests for ML feature contracts, metrics, and prediction loading rules."""

from __future__ import annotations

import unittest

import pandas as pd

from ml.data import (
    MODEL_FEATURE_COLUMNS,
    PCA_FEATURE_COLUMNS,
    build_features,
    validate_processed_modeling_frame,
)
from ml.evaluation import choose_best_model, evaluate_binary_classifier
from scripts.load_fraud_predictions_to_postgres import (
    normalize_database_url,
    validate_prediction_chunk,
)


def make_modeling_frame() -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "transaction_id": [f"TXN-{index:04d}" for index in range(6)],
            "Time": [0, 3600, 7200, 43_200, 82_800, 86_399],
            "Amount": [10.0, 20.0, 100.0, 250.0, 1_000.0, 50.0],
            "Class": [0, 0, 1, 0, 1, 0],
            "risk_score": [5, 10, 95, 20, 99, 15],
        }
    )
    for index, column in enumerate(PCA_FEATURE_COLUMNS, start=1):
        frame[column] = index / 10.0
    return frame


class MLFeatureContractTest(unittest.TestCase):
    def test_build_features_excludes_label_leakage_columns(self) -> None:
        frame = make_modeling_frame()
        validate_processed_modeling_frame(frame)

        features = build_features(frame)

        self.assertEqual(list(features.columns), MODEL_FEATURE_COLUMNS)
        self.assertNotIn("risk_score", features.columns)
        self.assertNotIn("Class", features.columns)
        self.assertNotIn("transaction_id", features.columns)
        self.assertIn("amount_log", features.columns)
        self.assertIn("hour_of_day", features.columns)
        self.assertIn("is_night_transaction", features.columns)

    def test_invalid_target_label_fails_validation(self) -> None:
        frame = make_modeling_frame()
        frame.loc[2, "Class"] = 3

        with self.assertRaises(ValueError):
            validate_processed_modeling_frame(frame)


class MLEvaluationTest(unittest.TestCase):
    def test_evaluate_binary_classifier_returns_required_metrics(self) -> None:
        metrics = evaluate_binary_classifier(
            y_true=[0, 0, 1, 1],
            fraud_probabilities=[0.05, 0.25, 0.80, 0.90],
            decision_threshold=0.50,
        )

        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["f1_score"], 1.0)
        self.assertEqual(metrics["roc_auc"], 1.0)
        self.assertEqual(metrics["confusion_matrix"]["true_positive"], 2)

    def test_choose_best_model_uses_f1_then_recall_then_auc(self) -> None:
        best_model = choose_best_model(
            {
                "a": {"f1_score": 0.7, "recall": 0.9, "roc_auc": 0.8},
                "b": {"f1_score": 0.8, "recall": 0.5, "roc_auc": 0.9},
            }
        )

        self.assertEqual(best_model, "b")


class PredictionLoaderContractTest(unittest.TestCase):
    def test_prediction_chunk_validation_accepts_valid_export(self) -> None:
        chunk = pd.DataFrame(
            {
                "transaction_id": ["TXN-1", "TXN-2"],
                "model_name": ["fraud_detection_classifier"] * 2,
                "model_version": ["1.0.0"] * 2,
                "fraud_probability": [0.01, 0.99],
                "predicted_class": [0, 1],
                "prediction_threshold": [0.5, 0.5],
            }
        )

        validate_prediction_chunk(chunk)

    def test_prediction_chunk_validation_rejects_invalid_probability(self) -> None:
        chunk = pd.DataFrame(
            {
                "transaction_id": ["TXN-1"],
                "model_name": ["fraud_detection_classifier"],
                "model_version": ["1.0.0"],
                "fraud_probability": [1.2],
                "predicted_class": [1],
                "prediction_threshold": [0.5],
            }
        )

        with self.assertRaises(ValueError):
            validate_prediction_chunk(chunk)

    def test_database_url_normalization_supports_sqlalchemy_driver_names(self) -> None:
        normalized = normalize_database_url(
            "postgresql+psycopg2://user:pass@localhost:5432/db"
        )

        self.assertEqual(normalized, "postgresql://user:pass@localhost:5432/db")


if __name__ == "__main__":
    unittest.main()
