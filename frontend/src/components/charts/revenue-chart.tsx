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
import { formatCurrency } from "@/lib/utils";

export function RevenueChart({ data }: { data: RevenueTrendPoint[] }) {
  const ordered = [...data].reverse();

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={ordered} margin={{ left: 0, right: 16, top: 10, bottom: 0 }}>
        <defs>
          <linearGradient id="revenue" x1="0" x2="0" y1="0" y2="1">
            <stop offset="5%" stopColor="#19c2a6" stopOpacity={0.45} />
            <stop offset="95%" stopColor="#19c2a6" stopOpacity={0.04} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#223044" vertical={false} />
        <XAxis dataKey="metric_date" tickLine={false} axisLine={false} />
        <YAxis tickLine={false} axisLine={false} tickFormatter={formatCurrency} />
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
