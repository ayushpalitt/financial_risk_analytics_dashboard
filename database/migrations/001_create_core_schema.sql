BEGIN;

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(16) PRIMARY KEY,
    customer_segment VARCHAR(40) NOT NULL,
    card_type VARCHAR(30) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_customers_id_format CHECK (customer_id LIKE 'CUST-%'),
    CONSTRAINT chk_customers_segment CHECK (
        customer_segment IN (
            'Mass Market',
            'Affluent',
            'Premium',
            'Small Business',
            'Student'
        )
    ),
    CONSTRAINT chk_customers_card_type CHECK (
        card_type IN ('Credit', 'Debit', 'Prepaid', 'Corporate')
    ),
    CONSTRAINT chk_customers_state_length CHECK (LENGTH(state) = 2)
);

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id VARCHAR(16) PRIMARY KEY,
    merchant_name VARCHAR(160) NOT NULL,
    merchant_category VARCHAR(60) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_merchants_id_format CHECK (merchant_id LIKE 'MRCH-%'),
    CONSTRAINT chk_merchants_category CHECK (
        merchant_category IN (
            'Grocery',
            'Fuel',
            'Travel',
            'Electronics',
            'Dining',
            'Entertainment',
            'Healthcare',
            'Utilities',
            'E-commerce',
            'Financial Services',
            'Luxury Retail'
        )
    )
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(32) PRIMARY KEY,
    source_row_number INTEGER NOT NULL UNIQUE,
    transaction_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    customer_id VARCHAR(16) NOT NULL REFERENCES customers(customer_id),
    merchant_id VARCHAR(16) NOT NULL REFERENCES merchants(merchant_id),
    transaction_channel VARCHAR(40) NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    class_label SMALLINT NOT NULL,
    is_fraud BOOLEAN NOT NULL,
    time_seconds INTEGER NOT NULL,
    approval_status VARCHAR(30) NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL,
    fraud_loss_amount NUMERIC(14, 2)
        GENERATED ALWAYS AS (
            CASE WHEN is_fraud THEN amount ELSE 0 END
        ) STORED,
    v1 DOUBLE PRECISION NOT NULL,
    v2 DOUBLE PRECISION NOT NULL,
    v3 DOUBLE PRECISION NOT NULL,
    v4 DOUBLE PRECISION NOT NULL,
    v5 DOUBLE PRECISION NOT NULL,
    v6 DOUBLE PRECISION NOT NULL,
    v7 DOUBLE PRECISION NOT NULL,
    v8 DOUBLE PRECISION NOT NULL,
    v9 DOUBLE PRECISION NOT NULL,
    v10 DOUBLE PRECISION NOT NULL,
    v11 DOUBLE PRECISION NOT NULL,
    v12 DOUBLE PRECISION NOT NULL,
    v13 DOUBLE PRECISION NOT NULL,
    v14 DOUBLE PRECISION NOT NULL,
    v15 DOUBLE PRECISION NOT NULL,
    v16 DOUBLE PRECISION NOT NULL,
    v17 DOUBLE PRECISION NOT NULL,
    v18 DOUBLE PRECISION NOT NULL,
    v19 DOUBLE PRECISION NOT NULL,
    v20 DOUBLE PRECISION NOT NULL,
    v21 DOUBLE PRECISION NOT NULL,
    v22 DOUBLE PRECISION NOT NULL,
    v23 DOUBLE PRECISION NOT NULL,
    v24 DOUBLE PRECISION NOT NULL,
    v25 DOUBLE PRECISION NOT NULL,
    v26 DOUBLE PRECISION NOT NULL,
    v27 DOUBLE PRECISION NOT NULL,
    v28 DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_transactions_id_format CHECK (transaction_id LIKE 'TXN-%'),
    CONSTRAINT chk_transactions_amount CHECK (amount >= 0),
    CONSTRAINT chk_transactions_class CHECK (class_label IN (0, 1)),
    CONSTRAINT chk_transactions_class_fraud_alignment CHECK (
        (class_label = 1 AND is_fraud = TRUE)
        OR (class_label = 0 AND is_fraud = FALSE)
    ),
    CONSTRAINT chk_transactions_time CHECK (time_seconds >= 0),
    CONSTRAINT chk_transactions_risk_score CHECK (risk_score BETWEEN 0 AND 100),
    CONSTRAINT chk_transactions_channel CHECK (
        transaction_channel IN (
            'Card Present',
            'E-commerce',
            'Mobile Wallet',
            'ATM',
            'Recurring'
        )
    ),
    CONSTRAINT chk_transactions_approval_status CHECK (
        approval_status IN ('Approved', 'Manual Review', 'Declined')
    )
);

CREATE TABLE IF NOT EXISTS fraud_predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(32) NOT NULL REFERENCES transactions(transaction_id),
    model_name VARCHAR(80) NOT NULL,
    model_version VARCHAR(40) NOT NULL,
    fraud_probability NUMERIC(7, 6) NOT NULL,
    predicted_class SMALLINT NOT NULL,
    prediction_threshold NUMERIC(7, 6) NOT NULL DEFAULT 0.500000,
    prediction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fraud_predictions_transaction_model UNIQUE (
        transaction_id,
        model_name,
        model_version
    ),
    CONSTRAINT chk_fraud_predictions_probability CHECK (
        fraud_probability BETWEEN 0 AND 1
    ),
    CONSTRAINT chk_fraud_predictions_class CHECK (predicted_class IN (0, 1)),
    CONSTRAINT chk_fraud_predictions_threshold CHECK (
        prediction_threshold BETWEEN 0 AND 1
    )
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    metric_date DATE PRIMARY KEY,
    total_transactions INTEGER NOT NULL,
    genuine_transactions INTEGER NOT NULL,
    fraud_transactions INTEGER NOT NULL,
    total_revenue NUMERIC(16, 2) NOT NULL,
    fraud_loss NUMERIC(16, 2) NOT NULL,
    average_transaction_value NUMERIC(14, 2) NOT NULL,
    fraud_rate NUMERIC(10, 6) NOT NULL,
    high_risk_transactions INTEGER NOT NULL,
    manual_review_transactions INTEGER NOT NULL,
    declined_transactions INTEGER NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_daily_metrics_non_negative_counts CHECK (
        total_transactions >= 0
        AND genuine_transactions >= 0
        AND fraud_transactions >= 0
        AND high_risk_transactions >= 0
        AND manual_review_transactions >= 0
        AND declined_transactions >= 0
    ),
    CONSTRAINT chk_daily_metrics_fraud_rate CHECK (fraud_rate BETWEEN 0 AND 1),
    CONSTRAINT chk_daily_metrics_revenue CHECK (
        total_revenue >= 0
        AND fraud_loss >= 0
        AND average_transaction_value >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_customers_segment
    ON customers(customer_segment);

CREATE INDEX IF NOT EXISTS idx_customers_state
    ON customers(state);

CREATE INDEX IF NOT EXISTS idx_merchants_category
    ON merchants(merchant_category);

CREATE INDEX IF NOT EXISTS idx_transactions_transaction_date
    ON transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_transactions_customer_date
    ON transactions(customer_id, transaction_date DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_merchant_date
    ON transactions(merchant_id, transaction_date DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_fraud_date
    ON transactions(is_fraud, transaction_date DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_risk_score
    ON transactions(risk_score DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_approval_status
    ON transactions(approval_status);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_transaction
    ON fraud_predictions(transaction_id);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_model_version
    ON fraud_predictions(model_name, model_version);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_customers_updated_at ON customers;
CREATE TRIGGER trg_customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_merchants_updated_at ON merchants;
CREATE TRIGGER trg_merchants_updated_at
BEFORE UPDATE ON merchants
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE FUNCTION refresh_daily_metrics()
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_metrics (
        metric_date,
        total_transactions,
        genuine_transactions,
        fraud_transactions,
        total_revenue,
        fraud_loss,
        average_transaction_value,
        fraud_rate,
        high_risk_transactions,
        manual_review_transactions,
        declined_transactions,
        updated_at
    )
    SELECT
        DATE(transaction_date) AS metric_date,
        COUNT(*)::INTEGER AS total_transactions,
        COUNT(*) FILTER (WHERE is_fraud = FALSE)::INTEGER AS genuine_transactions,
        COUNT(*) FILTER (WHERE is_fraud = TRUE)::INTEGER AS fraud_transactions,
        COALESCE(ROUND(SUM(amount), 2), 0)::NUMERIC(16, 2) AS total_revenue,
        COALESCE(ROUND(SUM(fraud_loss_amount), 2), 0)::NUMERIC(16, 2)
            AS fraud_loss,
        COALESCE(ROUND(AVG(amount), 2), 0)::NUMERIC(14, 2)
            AS average_transaction_value,
        COALESCE(
            ROUND(
                COUNT(*) FILTER (WHERE is_fraud = TRUE)::NUMERIC
                / NULLIF(COUNT(*), 0),
                6
            ),
            0
        )::NUMERIC(10, 6) AS fraud_rate,
        COUNT(*) FILTER (WHERE risk_score >= 70)::INTEGER
            AS high_risk_transactions,
        COUNT(*) FILTER (WHERE approval_status = 'Manual Review')::INTEGER
            AS manual_review_transactions,
        COUNT(*) FILTER (WHERE approval_status = 'Declined')::INTEGER
            AS declined_transactions,
        NOW() AS updated_at
    FROM transactions
    GROUP BY DATE(transaction_date)
    ON CONFLICT (metric_date)
    DO UPDATE SET
        total_transactions = EXCLUDED.total_transactions,
        genuine_transactions = EXCLUDED.genuine_transactions,
        fraud_transactions = EXCLUDED.fraud_transactions,
        total_revenue = EXCLUDED.total_revenue,
        fraud_loss = EXCLUDED.fraud_loss,
        average_transaction_value = EXCLUDED.average_transaction_value,
        fraud_rate = EXCLUDED.fraud_rate,
        high_risk_transactions = EXCLUDED.high_risk_transactions,
        manual_review_transactions = EXCLUDED.manual_review_transactions,
        declined_transactions = EXCLUDED.declined_transactions,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

COMMIT;
