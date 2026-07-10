"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { CustomerSegmentPoint, MerchantCategoryPoint } from "@/lib/types";
import {
  formatCompactCurrency,
  formatCompactNumber,
  formatCurrency,
  truncateChartLabel,
} from "@/lib/utils";

export function CategoryBarChart({
  data,
  labelKey,
  valueKey,
  color = "#9b8cff",
}: {
  data: Array<CustomerSegmentPoint | MerchantCategoryPoint>;
  labelKey: "customer_segment" | "merchant_category";
  valueKey: "revenue" | "transactions" | "fraud_loss";
  color?: string;
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ left: 12, right: 24, top: 12, bottom: 22 }}>
        <CartesianGrid stroke="#223044" vertical={false} />
        <XAxis
          dataKey={labelKey}
          tickLine={false}
          axisLine={false}
          interval={0}
          height={74}
          tickMargin={12}
          angle={-24}
          textAnchor="end"
          tick={{ fill: "#8fa0b5", fontSize: 11 }}
          tickFormatter={(value: string) => truncateChartLabel(value)}
        />
        <YAxis
          width={78}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tick={{ fill: "#8fa0b5", fontSize: 12 }}
          tickFormatter={(value: number) =>
            valueKey === "transactions"
              ? formatCompactNumber(value)
              : formatCompactCurrency(value)
          }
        />
        <Tooltip
          contentStyle={{
            background: "#0f1722",
            border: "1px solid #2b3b50",
            borderRadius: 8,
          }}
          formatter={(value) =>
            valueKey === "transactions"
              ? Number(value ?? 0).toLocaleString()
              : formatCurrency(Number(value ?? 0))
          }
        />
        <Bar dataKey={valueKey} fill={color} radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
