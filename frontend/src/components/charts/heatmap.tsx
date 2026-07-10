import type { FraudHeatmapPoint } from "@/lib/types";
import { formatPercent } from "@/lib/utils";

export function FraudHeatmap({ data }: { data: FraudHeatmapPoint[] }) {
  const maxRate = Math.max(...data.map((item) => item.fraud_rate), 0.001);

  return (
    <div className="grid h-full grid-cols-2 gap-2 overflow-hidden sm:grid-cols-3 lg:grid-cols-4">
      {data.slice(0, 24).map((item) => {
        const intensity = Math.min(item.fraud_rate / maxRate, 1);
        return (
          <div
            key={`${item.state}-${item.iso_day_of_week}-${item.hour_of_day}`}
            className="rounded-md border border-[#263345] p-3"
            style={{
              background: `rgba(239, 95, 122, ${0.08 + intensity * 0.28})`,
            }}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-semibold text-[#f5f8ff]">
                {item.state}
              </span>
              <span className="text-xs text-[#ffd27a]">
                {formatPercent(item.fraud_rate)}
              </span>
            </div>
            <div className="mt-2 text-xs text-[#a8b4c5]">
              D{item.iso_day_of_week} · {item.hour_of_day}:00
            </div>
            <div className="mt-1 text-xs text-[#a8b4c5]">
              {item.fraud_transactions} / {item.transactions}
            </div>
          </div>
        );
      })}
    </div>
  );
}
