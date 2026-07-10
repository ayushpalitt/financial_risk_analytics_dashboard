SELECT refresh_daily_metrics();

REFRESH MATERIALIZED VIEW mv_daily_metrics;
REFRESH MATERIALIZED VIEW mv_monthly_revenue;
REFRESH MATERIALIZED VIEW mv_rolling_fraud_rate;
REFRESH MATERIALIZED VIEW mv_top_customers_90d;
REFRESH MATERIALIZED VIEW mv_top_merchants_90d;
REFRESH MATERIALIZED VIEW mv_customer_lifetime_value;
REFRESH MATERIALIZED VIEW mv_merchant_risk_summary;
REFRESH MATERIALIZED VIEW mv_hourly_fraud_trend;
