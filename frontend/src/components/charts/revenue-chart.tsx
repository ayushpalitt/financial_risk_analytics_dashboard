"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { RevenueTrendPoint } from "@/lib/types";
import {
  formatChartDate,
  formatCompactCurrency,
  formatCurrency,
} from "@/lib/utils";

export function RevenueChart({ data }: { data: RevenueTrendPoint[] }) {
  const ordered = [...data].reverse();

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={ordered} margin={{ left: 12, right: 24, top: 12, bottom: 18 }}>
        <defs>
          <linearGradient id="revenue" x1="0" x2="0" y1="0" y2="1">
            <stop offset="5%" stopColor="#19c2a6" stopOpacity={0.45} />
            <stop offset="95%" stopColor="#19c2a6" stopOpacity={0.04} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#223044" vertical={false} />
        <XAxis
          dataKey="metric_date"
          tickLine={false}
          axisLine={false}
          tickMargin={10}
          tick={{ fill: "#8fa0b5", fontSize: 12 }}
          tickFormatter={formatChartDate}
        />
        <YAxis
          width={78}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tick={{ fill: "#8fa0b5", fontSize: 12 }}
          tickFormatter={formatCompactCurrency}
        />
        <Tooltip
          cursor={{ stroke: "#334155" }}
          contentStyle={{
            background: "#0f1722",
            border: "1px solid #2b3b50",
            borderRadius: 8,
          }}
          formatter={(value) => formatCurrency(Number(value ?? 0))}
        />
        <Area
          dataKey="revenue"
          stroke="#19c2a6"
          strokeWidth={2}
          fill="url(#revenue)"
          type="monotone"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
