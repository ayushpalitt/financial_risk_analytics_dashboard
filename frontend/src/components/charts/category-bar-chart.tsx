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
import { formatCurrency } from "@/lib/utils";

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
      <BarChart data={data} margin={{ left: 0, right: 16, top: 10, bottom: 0 }}>
        <CartesianGrid stroke="#223044" vertical={false} />
        <XAxis
          dataKey={labelKey}
          tickLine={false}
          axisLine={false}
          interval={0}
          height={70}
          tick={{ fontSize: 11 }}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tickFormatter={(value: number) =>
            valueKey === "transactions" ? `${Math.round(value / 1000)}k` : formatCurrency(value)
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
