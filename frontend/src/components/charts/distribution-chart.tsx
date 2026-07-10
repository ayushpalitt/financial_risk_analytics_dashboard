"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { FraudDistributionPoint } from "@/lib/types";
import { formatNumber, formatPercent } from "@/lib/utils";

const colors = ["#19c2a6", "#ef5f7a"];

export function DistributionChart({ data }: { data: FraudDistributionPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          dataKey="transactions"
          nameKey="class_name"
          innerRadius="58%"
          outerRadius="84%"
          paddingAngle={2}
        >
          {data.map((item, index) => (
            <Cell key={item.class_name} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "#0f1722",
            border: "1px solid #2b3b50",
            borderRadius: 8,
          }}
          formatter={(value, _name, payload) => {
            const item = payload.payload as FraudDistributionPoint;
            return [
              `${formatNumber(Number(value ?? 0))} (${formatPercent(item.transaction_share)})`,
              item.class_name,
            ];
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
