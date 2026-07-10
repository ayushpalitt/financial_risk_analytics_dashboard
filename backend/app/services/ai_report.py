"""Executive report generation service."""

from __future__ import annotations

import json
from typing import Any

from backend.app.core.config import Settings
from backend.app.db.repository import AnalyticsRepository


class ExecutiveReportService:
    """Build executive risk reports from current dashboard metrics."""

    def __init__(self, repository: AnalyticsRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    def collect_inputs(self) -> dict[str, Any]:
        """Collect compact dashboard inputs for report generation."""

        return {
            "overview": self._repository.dashboard_overview(),
            "fraud_trend": self._repository.fraud_trend(limit=14),
            "fraud_distribution": self._repository.fraud_distribution(),
            "customer_segments": self._repository.customer_segments(),
            "merchant_categories": self._repository.merchant_categories(),
            "top_customers": self._repository.top_customers(limit=5),
            "top_merchants": self._repository.top_merchants(limit=5),
            "model_performance": self._repository.model_performance(),
        }

    def generate_report(
        self,
        audience: str,
        include_recommendations: bool,
    ) -> dict[str, Any]:
        """Generate an AI report when configured, otherwise deterministic markdown."""

        inputs = self.collect_inputs()
        if self._settings.ai_reports_enabled and self._settings.openai_api_key:
            try:
                return {
                    "report_markdown": self._generate_openai_report(
                        inputs=inputs,
                        audience=audience,
                        include_recommendations=include_recommendations,
                    ),
                    "generated_with_ai": True,
                    "model": self._settings.openai_model,
                    "inputs": inputs,
                }
            except Exception as exc:  # pragma: no cover - defensive runtime fallback
                inputs["ai_generation_error"] = str(exc)

        return {
            "report_markdown": self._generate_fallback_report(
                inputs=inputs,
                audience=audience,
                include_recommendations=include_recommendations,
            ),
            "generated_with_ai": False,
            "model": None,
            "inputs": inputs,
        }

    def _generate_openai_report(
        self,
        inputs: dict[str, Any],
        audience: str,
        include_recommendations: bool,
    ) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self._settings.openai_api_key)
        response = client.responses.create(
            model=self._settings.openai_model,
            instructions=(
                "You are a senior financial risk analytics executive. "
                "Write concise Markdown for leadership using the provided KPI JSON. "
                "Include sections: Executive Summary, Business Risks, Fraud Analysis, "
                "Business Insights, and Recommendations. Avoid inventing metrics."
            ),
            input=json.dumps(
                {
                    "audience": audience,
                    "include_recommendations": include_recommendations,
                    "dashboard_inputs": inputs,
                },
                indent=2,
                sort_keys=True,
            ),
        )
        return str(response.output_text).strip()

    def _generate_fallback_report(
        self,
        inputs: dict[str, Any],
        audience: str,
        include_recommendations: bool,
    ) -> str:
        overview = inputs.get("overview", {})
        model = (inputs.get("model_performance") or [{}])[0]
        top_merchants = inputs.get("top_merchants") or []
        top_customers = inputs.get("top_customers") or []

        merchant_line = (
            f"{top_merchants[0]['merchant_name']} leads revenue exposure at "
            f"${top_merchants[0]['revenue']:,.2f}."
            if top_merchants
            else "Merchant concentration data is not available."
        )
        customer_line = (
            f"{top_customers[0]['customer_id']} is the top customer by spend at "
            f"${top_customers[0]['total_spend']:,.2f}."
            if top_customers
            else "Customer concentration data is not available."
        )

        recommendations = ""
        if include_recommendations:
            recommendations = (
                "\n## Recommendations\n"
                "- Prioritize manual review capacity around transactions with risk scores above 70.\n"
                "- Monitor merchant categories with elevated fraud rates before expanding approval rules.\n"
                "- Track model precision and recall after each retraining cycle.\n"
            )

        return (
            f"# Executive Risk Report\n\n"
            f"Audience: {audience}\n\n"
            "## Executive Summary\n"
            f"- Total transactions analyzed: {overview.get('total_transactions', 0):,}\n"
            f"- Revenue monitored: ${overview.get('revenue', 0):,.2f}\n"
            f"- Portfolio fraud rate: {overview.get('fraud_rate', 0):.4%}\n"
            f"- Fraud loss exposure: ${overview.get('fraud_loss', 0):,.2f}\n\n"
            "## Business Risks\n"
            f"- High-risk transactions: {overview.get('high_risk_transactions', 0):,}\n"
            f"- Average fraud amount: ${overview.get('average_fraud_amount', 0):,.2f}\n"
            f"- {merchant_line}\n\n"
            "## Fraud Analysis\n"
            f"- Model precision: {model.get('precision', 0):.2%}\n"
            f"- Model recall: {model.get('recall', 0):.2%}\n"
            f"- Model F1 score: {model.get('f1_score', 0):.2%}\n\n"
            "## Business Insights\n"
            f"- {customer_line}\n"
            "- Fraud monitoring is active across transaction, customer, merchant, and model layers.\n"
            f"{recommendations}"
        )
