CREATE OR REPLACE VIEW vw_dashboard_overview AS
SELECT
    COUNT(*)::BIGINT AS total_transactions,
    COALESCE(
        ROUND(
            COUNT(*) FILTER (WHERE is_fraud = TRUE)::NUMERIC
            / NULLIF(COUNT(*), 0),
            6
        ),
        0
    ) AS fraud_rate,
    COALESCE(ROUND(SUM(amount), 2), 0) AS revenue,
    COALESCE(ROUND(SUM(fraud_loss_amount), 2), 0) AS fraud_loss,
    COALESCE(ROUND(AVG(amount), 2), 0) AS average_transaction_value,
    COUNT(*) FILTER (WHERE risk_score >= 70)::BIGINT AS high_risk_transactions,
    COALESCE(ROUND(AVG(amount) FILTER (WHERE is_fraud = TRUE), 2), 0)
        AS average_fraud_amount
FROM transactions;

CREATE OR REPLACE VIEW vw_revenue_trend_daily AS
WITH daily_revenue AS (
    SELECT
        DATE(transaction_date) AS metric_date,
        COUNT(*)::BIGINT AS transaction_count,
        ROUND(SUM(amount), 2) AS revenue,
        ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss
    FROM transactions
    GROUP BY DATE(transaction_date)
)
SELECT
    metric_date,
    transaction_count,
    revenue,
    fraud_loss,
    SUM(revenue) OVER (
        ORDER BY metric_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_revenue,
    revenue - LAG(revenue) OVER (ORDER BY metric_date) AS revenue_delta
FROM daily_revenue;

CREATE OR REPLACE VIEW vw_fraud_trend_daily AS
WITH daily_fraud AS (
    SELECT
        DATE(transaction_date) AS metric_date,
        COUNT(*)::BIGINT AS transaction_count,
        COUNT(*) FILTER (WHERE is_fraud = TRUE)::BIGINT AS fraud_transactions,
        ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss
    FROM transactions
    GROUP BY DATE(transaction_date)
)
SELECT
    metric_date,
    transaction_count,
    fraud_transactions,
    fraud_loss,
    COALESCE(
        ROUND(fraud_transactions::NUMERIC / NULLIF(transaction_count, 0), 6),
        0
    ) AS fraud_rate,
    COALESCE(
        ROUND(
            AVG(fraud_transactions::NUMERIC / NULLIF(transaction_count, 0)) OVER (
                ORDER BY metric_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ),
            6
        ),
        0
    ) AS rolling_7_day_fraud_rate
FROM daily_fraud;

CREATE OR REPLACE VIEW vw_monthly_revenue AS
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', transaction_date)::DATE AS revenue_month,
        COUNT(*)::BIGINT AS transaction_count,
        ROUND(SUM(amount), 2) AS revenue,
        ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss
    FROM transactions
    GROUP BY DATE_TRUNC('month', transaction_date)::DATE
)
SELECT
    revenue_month,
    transaction_count,
    revenue,
    fraud_loss,
    SUM(revenue) OVER (
        ORDER BY revenue_month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM monthly_revenue;

CREATE OR REPLACE VIEW vw_customer_segments AS
SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_id)::BIGINT AS customers,
    COUNT(t.transaction_id)::BIGINT AS transactions,
    ROUND(SUM(t.amount), 2) AS revenue,
    ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
    COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
    COALESCE(
        ROUND(
            COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::NUMERIC
            / NULLIF(COUNT(*), 0),
            6
        ),
        0
    ) AS fraud_rate
FROM customers c
JOIN transactions t
    ON t.customer_id = c.customer_id
GROUP BY c.customer_segment;

CREATE OR REPLACE VIEW vw_merchant_categories AS
SELECT
    m.merchant_category,
    COUNT(DISTINCT m.merchant_id)::BIGINT AS merchants,
    COUNT(t.transaction_id)::BIGINT AS transactions,
    ROUND(SUM(t.amount), 2) AS revenue,
    ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
    ROUND(AVG(t.risk_score), 2) AS average_risk_score,
    COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
    COALESCE(
        ROUND(
            COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::NUMERIC
            / NULLIF(COUNT(*), 0),
            6
        ),
        0
    ) AS fraud_rate
FROM merchants m
JOIN transactions t
    ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_category;

CREATE OR REPLACE VIEW vw_fraud_distribution AS
SELECT
    class_label,
    CASE WHEN class_label = 1 THEN 'Fraud' ELSE 'Genuine' END AS class_name,
    COUNT(*)::BIGINT AS transactions,
    ROUND(SUM(amount), 2) AS revenue,
    ROUND(SUM(fraud_loss_amount), 2) AS fraud_loss,
    COALESCE(
        ROUND(COUNT(*)::NUMERIC / NULLIF(SUM(COUNT(*)) OVER (), 0), 6),
        0
    ) AS transaction_share
FROM transactions
GROUP BY class_label;

CREATE OR REPLACE VIEW vw_transaction_histogram AS
SELECT
    CASE
        WHEN amount < 25 THEN '0000-0024'
        WHEN amount < 50 THEN '0025-0049'
        WHEN amount < 100 THEN '0050-0099'
        WHEN amount < 250 THEN '0100-0249'
        WHEN amount < 500 THEN '0250-0499'
        WHEN amount < 1000 THEN '0500-0999'
        ELSE '1000+'
    END AS amount_bucket,
    COUNT(*)::BIGINT AS transactions,
    COUNT(*) FILTER (WHERE is_fraud = TRUE)::BIGINT AS fraud_transactions,
    ROUND(SUM(amount), 2) AS revenue
FROM transactions
GROUP BY amount_bucket;

CREATE OR REPLACE VIEW vw_fraud_heatmap AS
SELECT
    EXTRACT(ISODOW FROM transaction_date)::INTEGER AS iso_day_of_week,
    EXTRACT(HOUR FROM transaction_date)::INTEGER AS hour_of_day,
    c.state,
    COUNT(*)::BIGINT AS transactions,
    COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
    COALESCE(
        ROUND(
            COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::NUMERIC
            / NULLIF(COUNT(*), 0),
            6
        ),
        0
    ) AS fraud_rate,
    ROUND(AVG(t.risk_score), 2) AS average_risk_score
FROM transactions t
JOIN customers c
    ON c.customer_id = t.customer_id
GROUP BY
    EXTRACT(ISODOW FROM transaction_date)::INTEGER,
    EXTRACT(HOUR FROM transaction_date)::INTEGER,
    c.state;

CREATE OR REPLACE VIEW vw_latest_transactions AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
    ) AS latest_rank,
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.class_label,
    t.is_fraud,
    t.risk_score,
    t.approval_status,
    t.transaction_channel,
    c.customer_id,
    c.customer_segment,
    c.city,
    c.state,
    m.merchant_id,
    m.merchant_name,
    m.merchant_category
FROM transactions t
JOIN customers c
    ON c.customer_id = t.customer_id
JOIN merchants m
    ON m.merchant_id = t.merchant_id;

CREATE OR REPLACE VIEW vw_high_risk_transactions AS
SELECT
    DENSE_RANK() OVER (
        ORDER BY t.risk_score DESC, t.amount DESC, t.transaction_date DESC
    ) AS risk_rank,
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.class_label,
    t.is_fraud,
    t.risk_score,
    t.approval_status,
    t.transaction_channel,
    c.customer_segment,
    c.city,
    c.state,
    m.merchant_name,
    m.merchant_category
FROM transactions t
JOIN customers c
    ON c.customer_id = t.customer_id
JOIN merchants m
    ON m.merchant_id = t.merchant_id
WHERE t.risk_score >= 70
    OR t.is_fraud = TRUE
    OR t.approval_status IN ('Manual Review', 'Declined');

CREATE OR REPLACE VIEW vw_top_customers AS
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_segment,
        c.city,
        c.state,
        COUNT(t.transaction_id)::BIGINT AS transactions,
        ROUND(SUM(t.amount), 2) AS total_spend,
        ROUND(AVG(t.amount), 2) AS average_transaction_value,
        ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
        COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
        MAX(t.transaction_date) AS latest_transaction_at
    FROM customers c
    JOIN transactions t
        ON t.customer_id = c.customer_id
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
    average_transaction_value,
    fraud_loss,
    fraud_transactions,
    COALESCE(
        ROUND(fraud_transactions::NUMERIC / NULLIF(transactions, 0), 6),
        0
    ) AS fraud_rate,
    latest_transaction_at,
    DENSE_RANK() OVER (ORDER BY total_spend DESC) AS spend_rank,
    DENSE_RANK() OVER (
        ORDER BY fraud_transactions DESC, fraud_loss DESC, total_spend DESC
    ) AS fraud_exposure_rank
FROM customer_metrics;

CREATE OR REPLACE VIEW vw_top_merchants AS
WITH merchant_metrics AS (
    SELECT
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        COUNT(t.transaction_id)::BIGINT AS transactions,
        ROUND(SUM(t.amount), 2) AS revenue,
        ROUND(AVG(t.amount), 2) AS average_transaction_value,
        ROUND(AVG(t.risk_score), 2) AS average_risk_score,
        ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss,
        COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
        MAX(t.transaction_date) AS latest_transaction_at
    FROM merchants m
    JOIN transactions t
        ON t.merchant_id = m.merchant_id
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
    average_transaction_value,
    average_risk_score,
    fraud_loss,
    fraud_transactions,
    COALESCE(
        ROUND(fraud_transactions::NUMERIC / NULLIF(transactions, 0), 6),
        0
    ) AS fraud_rate,
    latest_transaction_at,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (
        ORDER BY fraud_transactions DESC, fraud_loss DESC, average_risk_score DESC
    ) AS fraud_risk_rank
FROM merchant_metrics;

CREATE OR REPLACE VIEW vw_customer_running_totals AS
SELECT
    t.customer_id,
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.is_fraud,
    SUM(t.amount) OVER (
        PARTITION BY t.customer_id
        ORDER BY t.transaction_date, t.transaction_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_customer_spend,
    SUM(t.fraud_loss_amount) OVER (
        PARTITION BY t.customer_id
        ORDER BY t.transaction_date, t.transaction_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_customer_fraud_loss,
    COUNT(*) OVER (
        PARTITION BY t.customer_id
        ORDER BY t.transaction_date, t.transaction_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_customer_transactions
FROM transactions t;

CREATE OR REPLACE VIEW vw_transaction_risk_rankings AS
SELECT
    t.transaction_id,
    DATE(t.transaction_date) AS transaction_day,
    m.merchant_category,
    t.amount,
    t.risk_score,
    t.is_fraud,
    t.approval_status,
    ROW_NUMBER() OVER (
        PARTITION BY DATE(t.transaction_date)
        ORDER BY t.risk_score DESC, t.amount DESC
    ) AS daily_risk_rank,
    DENSE_RANK() OVER (
        PARTITION BY m.merchant_category
        ORDER BY t.risk_score DESC, t.amount DESC
    ) AS category_risk_rank,
    PERCENT_RANK() OVER (
        ORDER BY t.risk_score ASC
    ) AS portfolio_risk_percentile
FROM transactions t
JOIN merchants m
    ON m.merchant_id = t.merchant_id;

CREATE OR REPLACE VIEW vw_merchant_fraud_trend AS
WITH merchant_daily AS (
    SELECT
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        DATE(t.transaction_date) AS metric_date,
        COUNT(*)::BIGINT AS transactions,
        COUNT(*) FILTER (WHERE t.is_fraud = TRUE)::BIGINT AS fraud_transactions,
        ROUND(SUM(t.fraud_loss_amount), 2) AS fraud_loss
    FROM transactions t
    JOIN merchants m
        ON m.merchant_id = t.merchant_id
    GROUP BY
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        DATE(t.transaction_date)
)
SELECT
    merchant_id,
    merchant_name,
    merchant_category,
    metric_date,
    transactions,
    fraud_transactions,
    fraud_loss,
    COALESCE(
        ROUND(fraud_transactions::NUMERIC / NULLIF(transactions, 0), 6),
        0
    ) AS fraud_rate,
    SUM(fraud_loss) OVER (
        PARTITION BY merchant_id
        ORDER BY metric_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_merchant_fraud_loss
FROM merchant_daily;

CREATE OR REPLACE VIEW vw_model_performance_by_version AS
WITH confusion_matrix AS (
    SELECT
        fp.model_name,
        fp.model_version,
        COUNT(*)::BIGINT AS predictions,
        SUM(
            CASE WHEN fp.predicted_class = 1 AND t.class_label = 1 THEN 1 ELSE 0 END
        )::BIGINT AS true_positive,
        SUM(
            CASE WHEN fp.predicted_class = 1 AND t.class_label = 0 THEN 1 ELSE 0 END
        )::BIGINT AS false_positive,
        SUM(
            CASE WHEN fp.predicted_class = 0 AND t.class_label = 0 THEN 1 ELSE 0 END
        )::BIGINT AS true_negative,
        SUM(
            CASE WHEN fp.predicted_class = 0 AND t.class_label = 1 THEN 1 ELSE 0 END
        )::BIGINT AS false_negative,
        ROUND(AVG(fp.fraud_probability), 6) AS average_fraud_probability,
        MAX(fp.prediction_date) AS latest_prediction_at
    FROM fraud_predictions fp
    JOIN transactions t
        ON t.transaction_id = fp.transaction_id
    GROUP BY fp.model_name, fp.model_version
)
SELECT
    model_name,
    model_version,
    predictions,
    true_positive,
    false_positive,
    true_negative,
    false_negative,
    COALESCE(
        ROUND((true_positive + true_negative)::NUMERIC / NULLIF(predictions, 0), 6),
        0
    ) AS accuracy,
    COALESCE(
        ROUND(true_positive::NUMERIC / NULLIF(true_positive + false_positive, 0), 6),
        0
    ) AS precision,
    COALESCE(
        ROUND(true_positive::NUMERIC / NULLIF(true_positive + false_negative, 0), 6),
        0
    ) AS recall,
    COALESCE(
        ROUND(
            (2 * true_positive)::NUMERIC
            / NULLIF((2 * true_positive) + false_positive + false_negative, 0),
            6
        ),
        0
    ) AS f1_score,
    average_fraud_probability,
    latest_prediction_at
FROM confusion_matrix;
