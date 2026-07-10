"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/tables/data-table";
import type { TopCustomer } from "@/lib/types";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";

const columns: ColumnDef<TopCustomer>[] = [
  { accessorKey: "spend_rank", header: "Rank" },
  {
    accessorKey: "customer_id",
    header: "Customer",
    cell: ({ row }) => (
      <span className="font-mono text-xs">{row.original.customer_id}</span>
    ),
  },
  {
    accessorKey: "customer_segment",
    header: "Segment",
    cell: ({ row }) => <Badge tone="violet">{row.original.customer_segment}</Badge>,
  },
  {
    accessorKey: "transactions",
    header: "Transactions",
    cell: ({ row }) => formatNumber(row.original.transactions),
  },
  {
    accessorKey: "total_spend",
    header: "Spend",
    cell: ({ row }) => formatCurrency(row.original.total_spend),
  },
  {
    accessorKey: "fraud_rate",
    header: "Fraud Rate",
    cell: ({ row }) => formatPercent(row.original.fraud_rate),
  },
  {
    accessorKey: "state",
    header: "Market",
    cell: ({ row }) => `${row.original.city}, ${row.original.state}`,
  },
];

export function CustomerTable({ data }: { data: TopCustomer[] }) {
  return <DataTable data={data} columns={columns} />;
}
