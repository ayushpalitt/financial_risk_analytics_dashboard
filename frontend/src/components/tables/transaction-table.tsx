"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/tables/data-table";
import type { TransactionRecord } from "@/lib/types";
import { formatCurrencyExact } from "@/lib/utils";

const columns: ColumnDef<TransactionRecord>[] = [
  {
    accessorKey: "transaction_id",
    header: "Transaction",
    cell: ({ row }) => (
      <span className="font-mono text-xs text-[#c6d1e1]">
        {row.original.transaction_id}
      </span>
    ),
  },
  {
    accessorKey: "transaction_date",
    header: "Date",
    cell: ({ row }) => (
      <span className="text-[#aeb9c8]">
        {row.original.transaction_date.replace("T", " ").slice(0, 16)}
      </span>
    ),
  },
  {
    accessorKey: "merchant_name",
    header: "Merchant",
  },
  {
    accessorKey: "merchant_category",
    header: "Category",
    cell: ({ row }) => <Badge tone="violet">{row.original.merchant_category}</Badge>,
  },
  {
    accessorKey: "amount",
    header: "Amount",
    cell: ({ row }) => formatCurrencyExact(row.original.amount),
  },
  {
    accessorKey: "risk_score",
    header: "Risk",
    cell: ({ row }) => (
      <Badge
        tone={
          row.original.risk_score >= 70
            ? "rose"
            : row.original.risk_score >= 45
              ? "amber"
              : "teal"
        }
      >
        {row.original.risk_score.toFixed(2)}
      </Badge>
    ),
  },
  {
    accessorKey: "approval_status",
    header: "Status",
    cell: ({ row }) => (
      <Badge
        tone={
          row.original.approval_status === "Approved"
            ? "teal"
            : row.original.approval_status === "Manual Review"
              ? "amber"
              : "rose"
        }
      >
        {row.original.approval_status}
      </Badge>
    ),
  },
];

export function TransactionTable({ data }: { data: TransactionRecord[] }) {
  return <DataTable data={data} columns={columns} />;
}
