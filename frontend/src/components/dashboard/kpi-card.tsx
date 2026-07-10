import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const toneMap = {
  teal: "text-[#7be5d1] bg-[#19c2a6]/10 border-[#19c2a6]/28",
  amber: "text-[#ffd27a] bg-[#f4b740]/10 border-[#f4b740]/28",
  rose: "text-[#ff9caf] bg-[#ef5f7a]/10 border-[#ef5f7a]/28",
  violet: "text-[#c5bdff] bg-[#9b8cff]/10 border-[#9b8cff]/28",
};

export function KpiCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = "teal",
}: {
  label: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  tone?: keyof typeof toneMap;
}) {
  return (
    <Card className="min-h-[132px]">
      <CardContent className="flex h-full flex-col justify-between">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-[0.08em] text-[#8fa0b5]">
              {label}
            </p>
            <p className="mt-2 truncate text-2xl font-semibold text-[#f4f8ff]">
              {value}
            </p>
          </div>
          <span
            className={cn(
              "grid h-10 w-10 shrink-0 place-items-center rounded-md border",
              toneMap[tone],
            )}
          >
            <Icon className="h-5 w-5" />
          </span>
        </div>
        <p className="mt-4 text-sm text-[#9aa8ba]">{detail}</p>
      </CardContent>
    </Card>
  );
}
