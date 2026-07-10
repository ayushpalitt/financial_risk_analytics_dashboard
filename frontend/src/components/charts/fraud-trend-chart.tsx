"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { FraudTrendPoint } from "@/lib/types";
import { formatPercent } from "@/lib/utils";

export function FraudTrendChart({ data }: { data: FraudTrendPoint[] }) {
  const ordered = [...data].reverse();

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={ordered} margin={{ left: 0, right: 16, top: 10, bottom: 0 }}>
        <CartesianGrid stroke="#223044" vertical={false} />
        <XAxis dataKey="metric_date" tickLine={false} axisLine={false} />
        <YAxis tickLine={false} axisLine={false} tickFormatter={formatPercent} />
        <Tooltip
          cursor={{ stroke: "#334155" }}
          contentStyle={{
            background: "#0f1722",
            border: "1px solid #2b3b50",
            borderRadius: 8,
          }}
          formatter={(value) => formatPercent(Number(value ?? 0))}
        />
        <Line
          dataKey="fraud_rate"
          stroke="#ef5f7a"
          strokeWidth={2}
          dot={false}
          type="monotone"
        />
        <Line
          dataKey="rolling_7_day_fraud_rate"
          stroke="#f4b740"
          strokeWidth={2}
          dot={false}
          type="monotone"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
