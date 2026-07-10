import { BrainCircuit, Gauge, Target, Trophy } from "lucide-react";

import { DistributionChart } from "@/components/charts/distribution-chart";
import { ChartCard } from "@/components/charts/chart-card";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { PageHeader } from "@/components/layout/page-header";
import { Reveal } from "@/components/motion/reveal";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getFraudDistribution, getModelPerformance } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function MachineLearningPage() {
  const [performance, distribution] = await Promise.all([
    getModelPerformance(),
    getFraudDistribution(),
  ]);
  const model = performance.items[0];

  return (
    <>
      <PageHeader title="Machine Learning" eyebrow="Fraud Model" />
      <Reveal>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label="Predictions"
            value={formatNumber(model?.predictions ?? 0)}
            detail="Scored transaction rows"
            icon={BrainCircuit}
            tone="violet"
          />
          <KpiCard
            label="Precision"
            value={formatPercent(model?.precision ?? 0)}
            detail="Predicted fraud quality"
            icon={Target}
            tone="teal"
          />
          <KpiCard
            label="Recall"
            value={formatPercent(model?.recall ?? 0)}
            detail="Fraud capture rate"
            icon={Gauge}
            tone="amber"
          />
          <KpiCard
            label="F1 Score"
            value={formatPercent(model?.f1_score ?? 0)}
            detail="Precision-recall balance"
            icon={Trophy}
            tone="rose"
          />
        </div>
      </Reveal>
      <div className="mt-5 grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
        <Reveal delay={0.05}>
          <ChartCard title="Fraud Distribution">
            <DistributionChart data={distribution} />
          </ChartCard>
        </Reveal>
        <Reveal delay={0.1}>
          <Card>
            <CardHeader>
              <CardTitle>Confusion Matrix</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <MetricTile label="True Positive" value={model?.true_positive ?? 0} tone="teal" />
                <MetricTile label="False Positive" value={model?.false_positive ?? 0} tone="amber" />
                <MetricTile label="False Negative" value={model?.false_negative ?? 0} tone="rose" />
                <MetricTile label="True Negative" value={model?.true_negative ?? 0} tone="violet" />
              </div>
              <div className="mt-5 border-t border-[#223044] pt-4 text-sm text-[#aeb9c8]">
                {model?.model_name ?? "fraud_detection_classifier"} · v
                {model?.model_version ?? "1.0.0"}
              </div>
            </CardContent>
          </Card>
        </Reveal>
      </div>
    </>
  );
}

function MetricTile({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "teal" | "amber" | "rose" | "violet";
}) {
  const color = {
    teal: "text-[#7be5d1]",
    amber: "text-[#ffd27a]",
    rose: "text-[#ff9caf]",
    violet: "text-[#c5bdff]",
  }[tone];

  return (
    <div className="rounded-md border border-[#263345] bg-[#131c29] p-4">
      <p className="text-xs uppercase tracking-[0.08em] text-[#8fa0b5]">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${color}`}>{formatNumber(value)}</p>
    </div>
  );
}
