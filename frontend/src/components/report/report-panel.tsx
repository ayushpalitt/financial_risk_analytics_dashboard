"use client";

import { useState, useTransition } from "react";
import { FileText, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { ExecutiveReportResponse } from "@/lib/types";

export function ReportPanel({
  initialReport,
}: {
  initialReport: ExecutiveReportResponse;
}) {
  const [report, setReport] = useState(initialReport);
  const [isPending, startTransition] = useTransition();

  function refreshReport() {
    startTransition(async () => {
      const response = await fetch("/api/ai-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          audience: "executive leadership",
          include_recommendations: true,
        }),
      });
      if (response.ok) {
        setReport((await response.json()) as ExecutiveReportResponse);
      }
    });
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
      <section className="rounded-lg border border-[#263345] bg-[#101620]/88 p-6">
        <div className="prose prose-invert max-w-none">
          <pre className="whitespace-pre-wrap text-sm leading-7 text-[#dce6f5]">
            {report.report_markdown}
          </pre>
        </div>
      </section>
      <aside className="rounded-lg border border-[#263345] bg-[#101620]/88 p-5">
        <div className="mb-5 flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-md border border-[#9b8cff]/35 bg-[#9b8cff]/10 text-[#c5bdff]">
            <FileText className="h-5 w-5" />
          </span>
          <div>
            <p className="text-sm font-semibold text-[#edf4ff]">
              {report.generated_with_ai ? "OpenAI" : "Deterministic"}
            </p>
            <p className="text-xs text-[#9aa8ba]">
              {report.model ?? "Local report builder"}
            </p>
          </div>
        </div>
        <Button
          className="w-full"
          onClick={refreshReport}
          disabled={isPending}
          title="Generate Executive Report"
        >
          <RefreshCw className="h-4 w-4" />
          {isPending ? "Generating" : "Generate Executive Report"}
        </Button>
      </aside>
    </div>
  );
}
