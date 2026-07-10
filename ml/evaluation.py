"""Model evaluation helpers for fraud classification."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_binary_classifier(
    y_true,
    fraud_probabilities,
    decision_threshold: float,
) -> dict[str, Any]:
    """Evaluate binary fraud predictions at a fixed decision threshold."""

    probabilities = np.asarray(fraud_probabilities, dtype=float)
    predictions = (probabilities >= decision_threshold).astype(int)
    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])

    return {
        "accuracy": round(float(accuracy_score(y_true, predictions)), 6),
        "precision": round(
            float(precision_score(y_true, predictions, zero_division=0)),
            6,
        ),
        "recall": round(
            float(recall_score(y_true, predictions, zero_division=0)),
            6,
        ),
        "f1_score": round(float(f1_score(y_true, predictions, zero_division=0)), 6),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 6),
        "confusion_matrix": {
            "labels": [0, 1],
            "matrix": matrix.tolist(),
            "true_negative": int(matrix[0, 0]),
            "false_positive": int(matrix[0, 1]),
            "false_negative": int(matrix[1, 0]),
            "true_positive": int(matrix[1, 1]),
        },
        "decision_threshold": decision_threshold,
    }


def choose_best_model(metrics_by_model: dict[str, dict[str, Any]]) -> str:
    """Select a model by F1 score, then recall, then ROC AUC."""

    if not metrics_by_model:
        raise ValueError("No model metrics were provided.")

    return max(
        metrics_by_model,
        key=lambda model_name: (
            metrics_by_model[model_name]["f1_score"],
            metrics_by_model[model_name]["recall"],
            metrics_by_model[model_name]["roc_auc"],
        ),
    )
