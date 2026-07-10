export type DashboardOverview = {
  total_transactions: number;
  fraud_rate: number;
  revenue: number;
  fraud_loss: number;
  average_transaction_value: number;
  high_risk_transactions: number;
  average_fraud_amount: number;
};

export type RevenueTrendPoint = {
  metric_date: string;
  transaction_count: number;
  revenue: number;
  fraud_loss: number;
  running_total_revenue: number;
  revenue_delta: number | null;
};

export type FraudTrendPoint = {
  metric_date: string;
  transaction_count: number;
  fraud_transactions: number;
  fraud_loss: number;
  fraud_rate: number;
  rolling_7_day_fraud_rate: number;
};

export type FraudDistributionPoint = {
  class_label: number;
  class_name: string;
  transactions: number;
  revenue: number;
  fraud_loss: number;
  transaction_share: number;
};

export type TransactionHistogramBucket = {
  amount_bucket: string;
  transactions: number;
  fraud_transactions: number;
  revenue: number;
};

export type FraudHeatmapPoint = {
  iso_day_of_week: number;
  hour_of_day: number;
  state: string;
  transactions: number;
  fraud_transactions: number;
  fraud_rate: number;
  average_risk_score: number;
};

export type CustomerSegmentPoint = {
  customer_segment: string;
  customers: number;
  transactions: number;
  revenue: number;
  fraud_loss: number;
  fraud_transactions: number;
  fraud_rate: number;
};

export type TopCustomer = {
  customer_id: string;
  customer_segment: string;
  city: string;
  state: string;
  transactions: number;
  total_spend: number;
  average_transaction_value: number;
  fraud_loss: number;
  fraud_transactions: number;
  fraud_rate: number;
  latest_transaction_at: string;
  spend_rank: number;
  fraud_exposure_rank: number;
};

export type MerchantCategoryPoint = {
  merchant_category: string;
  merchants: number;
  transactions: number;
  revenue: number;
  fraud_loss: number;
  average_risk_score: number;
  fraud_transactions: number;
  fraud_rate: number;
};

export type TopMerchant = {
  merchant_id: string;
  merchant_name: string;
  merchant_category: string;
  transactions: number;
  revenue: number;
  average_transaction_value: number;
  average_risk_score: number;
  fraud_loss: number;
  fraud_transactions: number;
  fraud_rate: number;
  latest_transaction_at: string;
  revenue_rank: number;
  fraud_risk_rank: number;
};

export type TransactionRecord = {
  transaction_id: string;
  transaction_date: string;
  amount: number;
  class_label: number;
  is_fraud: boolean;
  risk_score: number;
  approval_status: string;
  transaction_channel: string;
  customer_segment?: string | null;
  customer_id?: string | null;
  city?: string | null;
  state?: string | null;
  merchant_id?: string | null;
  merchant_name: string;
  merchant_category: string;
  latest_rank?: number | null;
  risk_rank?: number | null;
};

export type ModelPerformance = {
  model_name: string;
  model_version: string;
  predictions: number;
  true_positive: number;
  false_positive: number;
  true_negative: number;
  false_negative: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  average_fraud_probability: number;
  latest_prediction_at: string | null;
};

export type ExecutiveReportResponse = {
  report_markdown: string;
  generated_with_ai: boolean;
  model: string | null;
  inputs: Record<string, unknown>;
};
