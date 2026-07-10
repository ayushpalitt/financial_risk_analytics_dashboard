DROP MATERIALIZED VIEW IF EXISTS mv_hourly_fraud_trend;
DROP MATERIALIZED VIEW IF EXISTS mv_merchant_risk_summary;
DROP MATERIALIZED VIEW IF EXISTS mv_customer_lifetime_value;
DROP MATERIALIZED VIEW IF EXISTS mv_top_merchants_90d;
DROP MATERIALIZED VIEW IF EXISTS mv_top_customers_90d;
DROP MATERIALIZED VIEW IF EXISTS mv_rolling_fraud_rate;
DROP MATERIALIZED VIEW IF EXISTS mv_monthly_revenue;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_metrics;

CREATE MATERIALIZED VIEW mv_daily_metrics AS
SELECT
    DATE(transaction_date) AS metric_date,
    COUNT(*)::BIGINT AS total_transactions,
    COUNT(*) FILTER (WHERE is_fraud = FALSE)::BIGINT AS genuine_transactions,
    COUNT(*) FILTER (WHERE is_fraud = TRUE)::BIGINT AS fraud_transactions,
    ROUND(SUM(amount), 2) AS total_revenue,
    ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss,
    ROUND(AVG(amount), 2) AS average_transaction_value,
    COALESCE(
        ROUND(
            COUNT(*) FILTER (WHERE is_fraud = TRUE)::NUMERIC
            / NULLIF(COUNT(*), 0),
            6
        ),
        0
    ) AS fraud_rate,
    COUNT(*) FILTER (WHERE risk_score >= 70)::BIGINT AS high_risk_transactions,
    COUNT(*) FILTER (WHERE approval_status = 'Manual Review')::BIGINT
        AS manual_review_transactions,
    COUNT(*) FILTER (WHERE approval_status = 'Declined')::BIGINT
        AS declined_transactions
FROM transactions
GROUP BY DATE(transaction_date)
WITH DATA;

CREATE UNIQUE INDEX idx_mv_daily_metrics_date
    ON mv_daily_metrics(metric_date);

CREATE MATERIALIZED VIEW mv_monthly_revenue AS
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', transaction_date)::DATE AS revenue_month,
        COUNT(*)::BIGINT AS transactions,
        ROUND(SUM(amount), 2) AS revenue,
        ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss
    FROM transactions
    GROUP BY DATE_TRUNC('month', transaction_date)::DATE
)
SELECT
    revenue_month,
    transactions,
    revenue,
    fraud_loss,
    SUM(revenue) OVER (
        ORDER BY revenue_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM monthly_revenue
WITH DATA;

CREATE UNIQUE INDEX idx_mv_monthly_revenue_month
    ON mv_monthly_revenue(revenue_month);

CREATE MATERIALIZED VIEW mv_rolling_fraud_rate AS
WITH daily_fraud AS (
    SELECT
        DATE(transaction_date) AS metric_date,
        COUNT(*)::BIGINT AS transactions,
        COUNT(*) FILTER (WHERE is_fraud = TRUE)::BIGINT AS fraud_transactions,
        ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss
    FROM transactions
    GROUP BY DATE(transaction_date)
)
SELECT
    metric_date,
    transactions,
    fraud_transactions,
    fraud_loss,
    COALESCE(
        ROUND(fraud_transactions::NUMERIC / NULLIF(transactions, 0), 6),
        0
    ) AS fraud_rate,
    COALESCE(
        ROUND(
            AVG(fraud_transactions::NUMERIC / NULLIF(transactions, 0)) OVER (
                ORDER BY metric_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ),
            6
        ),
        0
    ) AS rolling_7_day_fraud_rate,
    SUM(fraud_loss) OVER (
        ORDER BY metric_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_fraud_loss
FROM daily_fraud
WITH DATA;

CREATE UNIQUE INDEX idx_mv_rolling_fraud_rate_date
    ON mv_rolling_fraud_rate(metric_date);

CREATE MATERIALIZED VIEW mv_top_customers_90d AS
WITH boundaries AS (
    SELECT MAX(transaction_date) AS max_transaction_date
    FROM transactions
),
customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_segment,
        c.city,
        c.state,
        COUNT(t.transaction_id)::BIGINT AS transactions,
        ROUND(SUM(t.amount), 2) AS total_spend,
        ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
        COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
        ROUND(AVG(t.risk_score), 2) AS average_risk_score
    FROM customers c
    JOIN transactions t
        ON t.customer_id = c.customer_id
    WHERE t.transaction_date >= COALESCE(
        (SELECT max_transaction_date - INTERVAL '90 days' FROM boundaries),
        TIMESTAMP '1900-01-01'
    )
    GROUP BY
        c.customer_id,
        c.customer_segment,
        c.city,
        c.state
)
SELECT
    customer_id,
    customer_segment,
    city,
    state,
    transactions,
    total_spend,
    fraud_loss,
    fraud_transactions,
    average_risk_score,
    DENSE_RANK() OVER (ORDER BY total_spend DESC) AS spend_rank,
    DENSE_RANK() OVER (
        ORDER BY fraud_transactions DESC, fraud_loss DESC, average_risk_score DESC
    ) AS fraud_exposure_rank
FROM customer_metrics
WITH DATA;

CREATE UNIQUE INDEX idx_mv_top_customers_90d_customer
    ON mv_top_customers_90d(customer_id);

CREATE INDEX idx_mv_top_customers_90d_spend_rank
    ON mv_top_customers_90d(spend_rank);

CREATE MATERIALIZED VIEW mv_top_merchants_90d AS
WITH boundaries AS (
    SELECT MAX(transaction_date) AS max_transaction_date
    FROM transactions
),
merchant_metrics AS (
    SELECT
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        COUNT(t.transaction_id)::BIGINT AS transactions,
        ROUND(SUM(t.amount), 2) AS revenue,
        ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
        COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
        ROUND(AVG(t.risk_score), 2) AS average_risk_score
    FROM merchants m
    JOIN transactions t
        ON t.merchant_id = m.merchant_id
    WHERE t.transaction_date >= COALESCE(
        (SELECT max_transaction_date - INTERVAL '90 days' FROM boundaries),
        TIMESTAMP '1900-01-01'
    )
    GROUP BY
        m.merchant_id,
        m.merchant_name,
        m.merchant_category
)
SELECT
    merchant_id,
    merchant_name,
    merchant_category,
    transactions,
    revenue,
    fraud_loss,
    fraud_transactions,
    average_risk_score,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (
        ORDER BY fraud_transactions DESC, fraud_loss DESC, average_risk_score DESC
    ) AS fraud_risk_rank
FROM merchant_metrics
WITH DATA;

CREATE UNIQUE INDEX idx_mv_top_merchants_90d_merchant
    ON mv_top_merchants_90d(merchant_id);

CREATE INDEX idx_mv_top_merchants_90d_revenue_rank
    ON mv_top_merchants_90d(revenue_rank);

CREATE MATERIALIZED VIEW mv_customer_lifetime_value AS
SELECT
    c.customer_id,
    c.customer_segment,
    c.city,
    c.state,
    COUNT(t.transaction_id)::BIGINT AS lifetime_transactions,
    ROUND(SUM(t.amount), 2) AS lifetime_value,
    ROUND(AVG(t.amount), 2) AS average_transaction_value,
    ROUND(SUM(t.fraud_loss_amount), 2) AS lifetime_fraud_loss,
    COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
    MIN(t.transaction_date) AS first_transaction_at,
    MAX(t.transaction_date) AS latest_transaction_at
FROM customers c
JOIN transactions t
    ON t.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.customer_segment,
    c.city,
    c.state
WITH DATA;

CREATE UNIQUE INDEX idx_mv_customer_lifetime_value_customer
    ON mv_customer_lifetime_value(customer_id);

CREATE INDEX idx_mv_customer_lifetime_value_value
    ON mv_customer_lifetime_value(lifetime_value DESC);

CREATE MATERIALIZED VIEW mv_merchant_risk_summary AS
SELECT
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    COUNT(t.transaction_id)::BIGINT AS transactions,
    ROUND(SUM(t.amount), 2) AS revenue,
    ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
    COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
    ROUND(AVG(t.risk_score), 2) AS average_risk_score,
    MAX(t.risk_score) AS maximum_risk_score
FROM merchants m
JOIN transactions t
    ON t.merchant_id = m.merchant_id
GROUP BY
    m.merchant_id,
    m.merchant_name,
    m.merchant_category
WITH DATA;

CREATE UNIQUE INDEX idx_mv_merchant_risk_summary_merchant
    ON mv_merchant_risk_summary(merchant_id);

CREATE INDEX idx_mv_merchant_risk_summary_risk
    ON mv_merchant_risk_summary(average_risk_score DESC);

CREATE MATERIALIZED VIEW mv_hourly_fraud_trend AS
SELECT
    DATE_TRUNC('hour', transaction_date) AS hour_bucket,
    COUNT(*)::BIGINT AS transactions,
    COUNT(*) FILTER (WHERE is_fraud = TRUE)::BIGINT AS fraud_transactions,
    ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss,
    COALESCE(
        ROUND(
            COUNT(*) FILTER (WHERE is_fraud = TRUE)::NUMERIC
            / NULLIF(COUNT(*), 0),
            6
        ),
        0
    ) AS fraud_rate,
    ROUND(AVG(risk_score), 2) AS average_risk_score
FROM transactions
GROUP BY DATE_TRUNC('hour', transaction_date)
WITH DATA;

CREATE UNIQUE INDEX idx_mv_hourly_fraud_trend_hour
    ON mv_hourly_fraud_trend(hour_bucket);
