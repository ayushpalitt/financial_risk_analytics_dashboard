import type {
  CustomerSegmentPoint,
  DashboardOverview,
  ExecutiveReportResponse,
  FraudDistributionPoint,
  FraudHeatmapPoint,
  FraudTrendPoint,
  MerchantCategoryPoint,
  ModelPerformance,
  RevenueTrendPoint,
  TopCustomer,
  TopMerchant,
  TransactionHistogramBucket,
  TransactionRecord,
} from "@/lib/types";

const API_BASE_URL =
  process.env.BACKEND_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8001";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${path} (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export function getOverview() {
  return getJson<DashboardOverview>("/dashboard/overview");
}

export async function getRevenue(limit = 90) {
  return getJson<{ items: RevenueTrendPoint[] }>(
    `/dashboard/revenue?limit=${limit}`,
  );
}

export async function getFraud(limit = 90, heatmapLimit = 500) {
  return getJson<{
    trend: FraudTrendPoint[];
    distribution: FraudDistributionPoint[];
    histogram: TransactionHistogramBucket[];
    heatmap: FraudHeatmapPoint[];
  }>(`/dashboard/fraud?limit=${limit}&heatmap_limit=${heatmapLimit}`);
}

export async function getCustomers(limit = 25) {
  return getJson<{
    segments: CustomerSegmentPoint[];
    top_customers: TopCustomer[];
  }>(`/dashboard/customers?limit=${limit}`);
}

export async function getTransactions(limit = 25) {
  return getJson<{
    latest_transactions: TransactionRecord[];
    high_risk_transactions: TransactionRecord[];
    top_merchants: TopMerchant[];
    merchant_categories: MerchantCategoryPoint[];
  }>(`/dashboard/transactions?limit=${limit}`);
}

export async function getModelPerformance() {
  return getJson<{ items: ModelPerformance[] }>("/ml/model-performance");
}

export async function getFraudDistribution() {
  return getJson<FraudDistributionPoint[]>("/ml/fraud-distribution");
}

export async function getExecutiveReport() {
  return getJson<ExecutiveReportResponse>("/ai/report");
}
