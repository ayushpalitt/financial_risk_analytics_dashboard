"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/tables/data-table";
import type { TopMerchant } from "@/lib/types";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";

const columns: ColumnDef<TopMerchant>[] = [
  { accessorKey: "revenue_rank", header: "Rank" },
  { accessorKey: "merchant_name", header: "Merchant" },
  {
    accessorKey: "merchant_category",
    header: "Category",
    cell: ({ row }) => <Badge tone="violet">{row.original.merchant_category}</Badge>,
  },
  {
    accessorKey: "transactions",
    header: "Transactions",
    cell: ({ row }) => formatNumber(row.original.transactions),
  },
  {
    accessorKey: "revenue",
    header: "Revenue",
    cell: ({ row }) => formatCurrency(row.original.revenue),
  },
  {
    accessorKey: "fraud_rate",
    header: "Fraud Rate",
    cell: ({ row }) => formatPercent(row.original.fraud_rate),
  },
  {
    accessorKey: "average_risk_score",
    header: "Avg Risk",
    cell: ({ row }) => row.original.average_risk_score.toFixed(2),
  },
];

export function MerchantTable({ data }: { data: TopMerchant[] }) {
  return <DataTable data={data} columns={columns} />;
}
