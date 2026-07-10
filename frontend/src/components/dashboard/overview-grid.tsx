import {
  AlertTriangle,
  BadgeDollarSign,
  CircleDollarSign,
  Percent,
  ReceiptText,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

import { KpiCard } from "@/components/dashboard/kpi-card";
import type { DashboardOverview } from "@/lib/types";
import {
  formatCurrency,
  formatCurrencyExact,
  formatNumber,
  formatPercent,
} from "@/lib/utils";

export function OverviewGrid({ overview }: { overview: DashboardOverview }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
      <KpiCard
        label="Total Transactions"
        value={formatNumber(overview.total_transactions)}
        detail="Processed portfolio activity"
        icon={ReceiptText}
        tone="teal"
      />
      <KpiCard
        label="Fraud Rate"
        value={formatPercent(overview.fraud_rate)}
        detail="Observed labeled fraud rate"
        icon={Percent}
        tone="rose"
      />
      <KpiCard
        label="Revenue"
        value={formatCurrency(overview.revenue)}
        detail="Transaction value monitored"
        icon={CircleDollarSign}
        tone="teal"
      />
      <KpiCard
        label="Fraud Loss"
        value={formatCurrency(overview.fraud_loss)}
        detail="Confirmed fraud exposure"
        icon={ShieldAlert}
        tone="rose"
      />
      <KpiCard
        label="Avg Transaction Value"
        value={formatCurrencyExact(overview.average_transaction_value)}
        detail="Portfolio mean ticket size"
        icon={TrendingUp}
        tone="violet"
      />
      <KpiCard
        label="High Risk Transactions"
        value={formatNumber(overview.high_risk_transactions)}
        detail="Risk score at or above 70"
        icon={AlertTriangle}
        tone="amber"
      />
      <KpiCard
        label="Avg Fraud Amount"
        value={formatCurrencyExact(overview.average_fraud_amount)}
        detail="Mean confirmed fraud amount"
        icon={BadgeDollarSign}
        tone="rose"
      />
    </div>
  );
}
