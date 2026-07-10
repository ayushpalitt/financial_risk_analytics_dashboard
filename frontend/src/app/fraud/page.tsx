import { ChartCard } from "@/components/charts/chart-card";
import { DistributionChart } from "@/components/charts/distribution-chart";
import { FraudHeatmap } from "@/components/charts/heatmap";
import { FraudTrendChart } from "@/components/charts/fraud-trend-chart";
import { PageHeader } from "@/components/layout/page-header";
import { Reveal } from "@/components/motion/reveal";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getFraud } from "@/lib/api";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function FraudPage() {
  const fraud = await getFraud(90, 96);
  const fraudClass = fraud.distribution.find((item) => item.class_label === 1);

  return (
    <>
      <PageHeader title="Fraud Analytics" eyebrow="Risk Intelligence" />
      <div className="grid gap-5 xl:grid-cols-[1.4fr_0.6fr]">
        <Reveal>
          <ChartCard title="Fraud Rate Trend">
            <FraudTrendChart data={fraud.trend} />
          </ChartCard>
        </Reveal>
        <Reveal delay={0.05}>
          <ChartCard title="Fraud Distribution">
            <DistributionChart data={fraud.distribution} />
          </ChartCard>
        </Reveal>
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Reveal delay={0.1}>
          <Card>
            <CardHeader>
              <CardTitle>Loss Snapshot</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between border-b border-[#223044] pb-3">
                <span className="text-sm text-[#9aa8ba]">Fraud Transactions</span>
                <span className="font-semibold text-[#edf4ff]">
                  {formatNumber(fraudClass?.transactions ?? 0)}
                </span>
              </div>
              <div className="flex items-center justify-between border-b border-[#223044] pb-3">
                <span className="text-sm text-[#9aa8ba]">Fraud Loss</span>
                <span className="font-semibold text-[#ff9caf]">
                  {formatCurrency(fraudClass?.fraud_loss ?? 0)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#9aa8ba]">Portfolio Share</span>
                <span className="font-semibold text-[#ffd27a]">
                  {formatPercent(fraudClass?.transaction_share ?? 0)}
                </span>
              </div>
            </CardContent>
          </Card>
        </Reveal>
        <Reveal delay={0.15}>
          <ChartCard title="Fraud Heatmap">
            <FraudHeatmap data={fraud.heatmap} />
          </ChartCard>
        </Reveal>
      </div>
    </>
  );
}
