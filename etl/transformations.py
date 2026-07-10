"""Deterministic data cleaning and enrichment transformations."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from etl.config import ETLConfig
from etl.schema import EXPECTED_RAW_COLUMNS, FEATURE_COLUMNS, validate_raw_schema


CUSTOMER_COUNT = 25_000
MERCHANT_COUNT = 750

CUSTOMER_SEGMENTS = np.array(
    ["Mass Market", "Affluent", "Premium", "Small Business", "Student"],
    dtype=object,
)
CUSTOMER_SEGMENT_PROBABILITIES = np.array([0.48, 0.22, 0.12, 0.11, 0.07])

CARD_TYPES = np.array(["Credit", "Debit", "Prepaid", "Corporate"], dtype=object)
TRANSACTION_CHANNELS = np.array(
    ["Card Present", "E-commerce", "Mobile Wallet", "ATM", "Recurring"],
    dtype=object,
)
TRANSACTION_CHANNEL_PROBABILITIES = np.array([0.46, 0.27, 0.16, 0.06, 0.05])

MERCHANT_CATEGORY_NAMES: dict[str, tuple[str, ...]] = {
    "Grocery": (
        "Northstar Grocers",
        "Metro Fresh Market",
        "Civic Pantry",
        "GreenBasket Foods",
    ),
    "Fuel": (
        "Atlas Fuel",
        "Summit Energy Stop",
        "Roadway Petroleum",
        "Union Auto Mart",
    ),
    "Travel": (
        "Apex Travel Group",
        "Harbor Airways",
        "Continental Hotels",
        "SkyRail Booking",
    ),
    "Electronics": (
        "Quantum Electronics",
        "Circuit Square",
        "NexGen Devices",
        "VoltPoint Retail",
    ),
    "Dining": (
        "Cedar Table",
        "Urban Plate",
        "Blue Harbor Cafe",
        "Market Street Bistro",
    ),
    "Entertainment": (
        "Premiere Events",
        "CineMax Venues",
        "BrightStage Tickets",
        "Playhouse Digital",
    ),
    "Healthcare": (
        "Meridian Pharmacy",
        "CarePlus Clinic",
        "WellPath Medical",
        "Prime Health Supply",
    ),
    "Utilities": (
        "Civic Power",
        "ClearWater Utility",
        "Metro Gas Services",
        "FiberLink Telecom",
    ),
    "E-commerce": (
        "Aster Online Marketplace",
        "ParcelCart",
        "Nova Direct",
        "RapidShop Digital",
    ),
    "Financial Services": (
        "Evergreen Insurance",
        "Pinnacle Lending",
        "Crestline Brokerage",
        "Union Remittance",
    ),
    "Luxury Retail": (
        "Luxe Avenue",
        "Sterling Jewelers",
        "Monarch Fashion",
        "Aurum Gallery",
    ),
}
MERCHANT_CATEGORIES = np.array(tuple(MERCHANT_CATEGORY_NAMES.keys()), dtype=object)
MERCHANT_CATEGORY_PROBABILITIES = np.array(
    [0.16, 0.08, 0.08, 0.09, 0.13, 0.06, 0.09, 0.07, 0.16, 0.05, 0.03]
)

US_LOCATIONS = np.array(
    [
        ("New York", "NY"),
        ("Los Angeles", "CA"),
        ("Chicago", "IL"),
        ("Houston", "TX"),
        ("Phoenix", "AZ"),
        ("Philadelphia", "PA"),
        ("San Antonio", "TX"),
        ("San Diego", "CA"),
        ("Dallas", "TX"),
        ("San Jose", "CA"),
        ("Austin", "TX"),
        ("Jacksonville", "FL"),
        ("Fort Worth", "TX"),
        ("Columbus", "OH"),
        ("Charlotte", "NC"),
        ("San Francisco", "CA"),
        ("Seattle", "WA"),
        ("Denver", "CO"),
        ("Washington", "DC"),
        ("Boston", "MA"),
        ("Miami", "FL"),
        ("Atlanta", "GA"),
        ("Minneapolis", "MN"),
        ("Detroit", "MI"),
        ("Las Vegas", "NV"),
    ],
    dtype=object,
)

CHANNEL_RISK_POINTS = {
    "Card Present": 3.0,
    "E-commerce": 8.0,
    "Mobile Wallet": 6.0,
    "ATM": 10.0,
    "Recurring": 4.0,
}
CATEGORY_RISK_POINTS = {
    "Grocery": 2.0,
    "Fuel": 4.0,
    "Travel": 8.0,
    "Electronics": 7.0,
    "Dining": 3.0,
    "Entertainment": 5.0,
    "Healthcare": 2.0,
    "Utilities": 2.0,
    "E-commerce": 8.0,
    "Financial Services": 7.0,
    "Luxury Retail": 10.0,
}

PROCESSED_COLUMN_ORDER = [
    "transaction_id",
    "source_row_number",
    "transaction_date",
    "customer_id",
    "merchant_id",
    "merchant_name",
    "merchant_category",
    "transaction_channel",
    "card_type",
    "city",
    "state",
    "customer_segment",
    "risk_score",
    "approval_status",
    "Time",
    "Amount",
    "Class",
    "is_fraud",
    *FEATURE_COLUMNS,
]


@dataclass(frozen=True)
class CleaningSummary:
    """Summary of cleaning operations applied before enrichment."""

    raw_rows: int
    rows_after_missing_value_drop: int
    duplicate_rows_detected: int
    processed_rows: int
    missing_values_by_column: dict[str, int]
    rows_dropped_for_missing_values: int
    rows_dropped_as_duplicates: int


def clean_transactions(raw_frame: pd.DataFrame) -> tuple[pd.DataFrame, CleaningSummary]:
    """Validate, de-duplicate, and type-normalize the raw transactions."""

    frame = raw_frame.copy()
    frame.columns = [column.strip() for column in frame.columns]
    validate_raw_schema(frame)

    missing_values = {
        column: int(count) for column, count in frame.isna().sum().to_dict().items()
    }
    duplicate_rows = int(frame.duplicated(subset=EXPECTED_RAW_COLUMNS).sum())

    frame = frame.copy()
    frame.insert(0, "source_row_number", np.arange(1, len(frame) + 1, dtype=np.int64))

    frame_without_missing = frame.dropna(subset=EXPECTED_RAW_COLUMNS).copy()
    rows_after_missing_drop = int(len(frame_without_missing))

    cleaned_frame = (
        frame_without_missing.drop_duplicates(subset=EXPECTED_RAW_COLUMNS, keep="first")
        .copy()
        .reset_index(drop=True)
    )

    cleaned_frame["Time"] = cleaned_frame["Time"].astype(np.int64)
    cleaned_frame["Amount"] = cleaned_frame["Amount"].astype(float)
    cleaned_frame["Class"] = cleaned_frame["Class"].astype(np.int8)

    summary = CleaningSummary(
        raw_rows=int(len(frame)),
        rows_after_missing_value_drop=rows_after_missing_drop,
        duplicate_rows_detected=duplicate_rows,
        processed_rows=int(len(cleaned_frame)),
        missing_values_by_column=missing_values,
        rows_dropped_for_missing_values=int(len(frame) - rows_after_missing_drop),
        rows_dropped_as_duplicates=int(rows_after_missing_drop - len(cleaned_frame)),
    )
    return cleaned_frame, summary


def enrich_transactions(
    cleaned_frame: pd.DataFrame,
    config: ETLConfig,
) -> pd.DataFrame:
    """Create deterministic business columns for enterprise analytics."""

    validate_raw_schema(cleaned_frame[EXPECTED_RAW_COLUMNS])

    frame = cleaned_frame.copy().reset_index(drop=True)
    rng = np.random.default_rng(config.random_seed)
    row_count = len(frame)

    customer_profiles = _build_customer_profiles(rng)
    merchant_catalog = _build_merchant_catalog(rng)

    customer_indices = _weighted_indices(rng, CUSTOMER_COUNT, row_count, shape=1.7)
    merchant_indices = _weighted_indices(rng, MERCHANT_COUNT, row_count, shape=1.5)

    frame["transaction_id"] = _build_transaction_ids(frame)
    frame["customer_id"] = customer_profiles["customer_id"][customer_indices]
    frame["customer_segment"] = customer_profiles["customer_segment"][customer_indices]
    frame["card_type"] = customer_profiles["card_type"][customer_indices]
    frame["city"] = customer_profiles["city"][customer_indices]
    frame["state"] = customer_profiles["state"][customer_indices]
    frame["merchant_id"] = merchant_catalog["merchant_id"][merchant_indices]
    frame["merchant_name"] = merchant_catalog["merchant_name"][merchant_indices]
    frame["merchant_category"] = merchant_catalog["merchant_category"][merchant_indices]
    frame["transaction_channel"] = _generate_transaction_channels(
        rng,
        frame["merchant_category"].to_numpy(dtype=object),
    )
    frame["transaction_date"] = _build_transaction_dates(
        frame["Time"],
        config.base_transaction_datetime,
    )
    frame["risk_score"] = _calculate_risk_scores(frame, rng)
    frame["approval_status"] = _build_approval_status(frame["risk_score"].to_numpy())
    frame["is_fraud"] = frame["Class"].astype(bool)

    return frame[PROCESSED_COLUMN_ORDER].copy()


def build_quality_report(
    raw_frame: pd.DataFrame,
    processed_frame: pd.DataFrame,
    cleaning_summary: CleaningSummary,
    config: ETLConfig,
    raw_file_sha256: str,
    processed_file_sha256: str,
) -> dict[str, Any]:
    """Create a serializable report for observability and auditability."""

    class_distribution = {
        str(label): int(count)
        for label, count in processed_frame["Class"]
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
        .items()
    }

    approval_distribution = {
        str(label): int(count)
        for label, count in processed_frame["approval_status"]
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
        .items()
    }

    risk_summary = processed_frame["risk_score"].describe(
        percentiles=[0.25, 0.5, 0.75, 0.95, 0.99]
    )
    amount_summary = processed_frame["Amount"].describe(
        percentiles=[0.25, 0.5, 0.75, 0.95, 0.99]
    )

    return {
        "dataset": {
            "raw_path": str(config.raw_data_path),
            "processed_path": str(config.processed_data_path),
            "raw_file_sha256": raw_file_sha256,
            "processed_file_sha256": processed_file_sha256,
            "random_seed": config.random_seed,
        },
        "schema": {
            "raw_columns": list(raw_frame.columns),
            "processed_columns": list(processed_frame.columns),
        },
        "cleaning": {
            "raw_rows": cleaning_summary.raw_rows,
            "rows_after_missing_value_drop": (
                cleaning_summary.rows_after_missing_value_drop
            ),
            "processed_rows": cleaning_summary.processed_rows,
            "duplicate_rows_detected": cleaning_summary.duplicate_rows_detected,
            "rows_dropped_for_missing_values": (
                cleaning_summary.rows_dropped_for_missing_values
            ),
            "rows_dropped_as_duplicates": cleaning_summary.rows_dropped_as_duplicates,
            "missing_values_by_column": cleaning_summary.missing_values_by_column,
        },
        "distributions": {
            "class": class_distribution,
            "approval_status": approval_distribution,
            "customer_segments": _value_counts(processed_frame, "customer_segment"),
            "merchant_categories": _value_counts(processed_frame, "merchant_category"),
            "transaction_channels": _value_counts(
                processed_frame,
                "transaction_channel",
            ),
            "card_types": _value_counts(processed_frame, "card_type"),
            "states": _value_counts(processed_frame, "state"),
        },
        "metrics": {
            "total_amount": round(float(processed_frame["Amount"].sum()), 2),
            "fraud_amount": round(
                float(processed_frame.loc[processed_frame["Class"] == 1, "Amount"].sum()),
                2,
            ),
            "fraud_rate": round(float(processed_frame["Class"].mean()), 6),
            "average_transaction_value": round(
                float(processed_frame["Amount"].mean()),
                2,
            ),
            "high_risk_transactions": int((processed_frame["risk_score"] >= 70).sum()),
        },
        "summaries": {
            "amount": _series_summary(amount_summary),
            "risk_score": _series_summary(risk_summary),
        },
    }


def _build_customer_profiles(rng: np.random.Generator) -> dict[str, np.ndarray]:
    location_indices = rng.integers(0, len(US_LOCATIONS), size=CUSTOMER_COUNT)
    segments = rng.choice(
        CUSTOMER_SEGMENTS,
        size=CUSTOMER_COUNT,
        p=CUSTOMER_SEGMENT_PROBABILITIES,
    )
    card_types = np.array(
        [_select_card_type_for_segment(segment, rng) for segment in segments],
        dtype=object,
    )

    return {
        "customer_id": np.array(
            [f"CUST-{index:07d}" for index in range(1, CUSTOMER_COUNT + 1)],
            dtype=object,
        ),
        "customer_segment": segments,
        "card_type": card_types,
        "city": US_LOCATIONS[location_indices, 0].astype(object),
        "state": US_LOCATIONS[location_indices, 1].astype(object),
    }


def _select_card_type_for_segment(
    segment: str,
    rng: np.random.Generator,
) -> str:
    if segment == "Small Business":
        probabilities = np.array([0.34, 0.12, 0.02, 0.52])
    elif segment == "Premium":
        probabilities = np.array([0.76, 0.13, 0.01, 0.10])
    elif segment == "Student":
        probabilities = np.array([0.28, 0.52, 0.18, 0.02])
    elif segment == "Affluent":
        probabilities = np.array([0.69, 0.23, 0.02, 0.06])
    else:
        probabilities = np.array([0.46, 0.42, 0.09, 0.03])
    return str(rng.choice(CARD_TYPES, p=probabilities))


def _build_merchant_catalog(rng: np.random.Generator) -> dict[str, np.ndarray]:
    merchant_categories = rng.choice(
        MERCHANT_CATEGORIES,
        size=MERCHANT_COUNT,
        p=MERCHANT_CATEGORY_PROBABILITIES,
    )
    merchant_names = []

    for index, category in enumerate(merchant_categories, start=1):
        name_options = MERCHANT_CATEGORY_NAMES[str(category)]
        base_name = str(rng.choice(name_options))
        merchant_names.append(f"{base_name} #{index:03d}")

    return {
        "merchant_id": np.array(
            [f"MRCH-{index:06d}" for index in range(1, MERCHANT_COUNT + 1)],
            dtype=object,
        ),
        "merchant_name": np.array(merchant_names, dtype=object),
        "merchant_category": merchant_categories.astype(object),
    }


def _weighted_indices(
    rng: np.random.Generator,
    population_size: int,
    sample_size: int,
    shape: float,
) -> np.ndarray:
    weights = rng.pareto(shape, size=population_size) + 1.0
    weights = weights / weights.sum()
    return rng.choice(population_size, size=sample_size, replace=True, p=weights)


def _build_transaction_ids(frame: pd.DataFrame) -> list[str]:
    transaction_ids = []
    for source_row, time_value, amount, class_label in zip(
        frame["source_row_number"].to_numpy(),
        frame["Time"].to_numpy(),
        frame["Amount"].to_numpy(),
        frame["Class"].to_numpy(),
    ):
        fingerprint = f"{int(source_row)}|{int(time_value)}|{float(amount):.2f}|{int(class_label)}"
        digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:18].upper()
        transaction_ids.append(f"TXN-{digest}")
    return transaction_ids


def _generate_transaction_channels(
    rng: np.random.Generator,
    merchant_categories: np.ndarray,
) -> np.ndarray:
    channels = rng.choice(
        TRANSACTION_CHANNELS,
        size=len(merchant_categories),
        p=TRANSACTION_CHANNEL_PROBABILITIES,
    ).astype(object)

    ecommerce_mask = merchant_categories == "E-commerce"
    travel_mask = merchant_categories == "Travel"
    if ecommerce_mask.any():
        channels[ecommerce_mask] = rng.choice(
            np.array(["E-commerce", "Mobile Wallet", "Recurring"], dtype=object),
            size=int(ecommerce_mask.sum()),
            p=np.array([0.74, 0.18, 0.08]),
        )
    if travel_mask.any():
        channels[travel_mask] = rng.choice(
            np.array(["Card Present", "E-commerce", "Mobile Wallet"], dtype=object),
            size=int(travel_mask.sum()),
            p=np.array([0.45, 0.38, 0.17]),
        )
    return channels


def _build_transaction_dates(
    time_seconds: pd.Series,
    base_transaction_datetime: str,
) -> pd.Series:
    dates = pd.to_datetime(base_transaction_datetime) + pd.to_timedelta(
        time_seconds.astype(np.int64),
        unit="s",
    )
    return dates.dt.strftime("%Y-%m-%d %H:%M:%S")


def _calculate_risk_scores(
    frame: pd.DataFrame,
    rng: np.random.Generator,
) -> np.ndarray:
    amounts = frame["Amount"].to_numpy(dtype=float)
    amount_denominator = max(float(np.log1p(amounts.max())), 1.0)
    amount_component = np.clip(np.log1p(amounts) / amount_denominator, 0, 1) * 24.0

    feature_matrix = frame[FEATURE_COLUMNS].to_numpy(dtype=float)
    anomaly_proxy = np.sqrt(np.square(feature_matrix).mean(axis=1))
    median = float(np.quantile(anomaly_proxy, 0.50))
    upper = float(np.quantile(anomaly_proxy, 0.99))
    anomaly_denominator = max(upper - median, 1e-9)
    anomaly_component = (
        np.clip((anomaly_proxy - median) / anomaly_denominator, 0, 1) * 28.0
    )

    channel_component = (
        frame["transaction_channel"].map(CHANNEL_RISK_POINTS).astype(float).to_numpy()
    )
    category_component = (
        frame["merchant_category"].map(CATEGORY_RISK_POINTS).astype(float).to_numpy()
    )
    historical_fraud_component = np.where(frame["Class"].to_numpy() == 1, 26.0, 0.0)
    seeded_jitter = rng.normal(loc=0.0, scale=1.4, size=len(frame))

    risk_score = (
        8.0
        + amount_component
        + anomaly_component
        + channel_component
        + category_component
        + historical_fraud_component
        + seeded_jitter
    )
    return np.round(np.clip(risk_score, 0.0, 100.0), 2)


def _build_approval_status(risk_scores: np.ndarray) -> np.ndarray:
    return np.select(
        [risk_scores >= 85.0, risk_scores >= 70.0],
        ["Declined", "Manual Review"],
        default="Approved",
    ).astype(object)


def _value_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    return {
        str(label): int(count)
        for label, count in frame[column]
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
        .items()
    }


def _series_summary(summary: pd.Series) -> dict[str, float]:
    return {str(label): round(float(value), 6) for label, value in summary.items()}
