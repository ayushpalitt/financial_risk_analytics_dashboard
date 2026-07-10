import { Activity, Database } from "lucide-react";

import { ChartCard } from "@/components/charts/chart-card";
import { CategoryBarChart } from "@/components/charts/category-bar-chart";
import { FraudTrendChart } from "@/components/charts/fraud-trend-chart";
import { RevenueChart } from "@/components/charts/revenue-chart";
import { OverviewGrid } from "@/components/dashboard/overview-grid";
import { PageHeader } from "@/components/layout/page-header";
import { Reveal } from "@/components/motion/reveal";
import { Card, CardContent } from "@/components/ui/card";
import {
  getCustomers,
  getFraud,
  getOverview,
  getRevenue,
  getTransactions,
} from "@/lib/api";
import { formatNumber } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [overview, revenue, fraud, customers, transactions] = await Promise.all([
    getOverview(),
    getRevenue(30),
    getFraud(30, 24),
    getCustomers(10),
    getTransactions(10),
  ]);

  return (
    <>
      <PageHeader title="Portfolio Command Center" eyebrow="Risk Operations">
        <div className="grid grid-cols-2 gap-3">
          <Card className="min-w-[160px]">
            <CardContent className="flex items-center gap-3 p-3">
              <Activity className="h-5 w-5 text-[#7be5d1]" />
              <div>
                <p className="text-xs text-[#9aa8ba]">Fraud Events</p>
                <p className="text-sm font-semibold text-[#edf4ff]">
                  {formatNumber(fraud.distribution.find((item) => item.class_label === 1)?.transactions ?? 0)}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card className="min-w-[160px]">
            <CardContent className="flex items-center gap-3 p-3">
              <Database className="h-5 w-5 text-[#ffd27a]" />
              <div>
                <p className="text-xs text-[#9aa8ba]">Merchants</p>
                <p className="text-sm font-semibold text-[#edf4ff]">
                  {formatNumber(transactions.merchant_categories.reduce((sum, item) => sum + item.merchants, 0))}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageHeader>
      <Reveal>
        <OverviewGrid overview={overview} />
      </Reveal>
      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Reveal delay={0.05}>
          <ChartCard title="Revenue Trend">
            <RevenueChart data={revenue.items} />
          </ChartCard>
        </Reveal>
        <Reveal delay={0.1}>
          <ChartCard title="Fraud Trend">
            <FraudTrendChart data={fraud.trend} />
          </ChartCard>
        </Reveal>
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Reveal delay={0.15}>
          <ChartCard title="Customer Segments">
            <CategoryBarChart
              data={customers.segments}
              labelKey="customer_segment"
              valueKey="revenue"
              color="#9b8cff"
            />
          </ChartCard>
        </Reveal>
        <Reveal delay={0.2}>
          <ChartCard title="Merchant Categories">
            <CategoryBarChart
              data={transactions.merchant_categories}
              labelKey="merchant_category"
              valueKey="revenue"
              color="#f4b740"
            />
          </ChartCard>
        </Reveal>
      </div>
    </>
  );
}
