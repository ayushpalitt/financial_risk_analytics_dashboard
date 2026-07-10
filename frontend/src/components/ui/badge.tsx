import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeTone = "teal" | "amber" | "rose" | "violet" | "muted";

const tones: Record<BadgeTone, string> = {
  teal: "border-[#19c2a6]/35 bg-[#19c2a6]/10 text-[#7be5d1]",
  amber: "border-[#f4b740]/35 bg-[#f4b740]/10 text-[#ffd27a]",
  rose: "border-[#ef5f7a]/35 bg-[#ef5f7a]/10 text-[#ff9caf]",
  violet: "border-[#9b8cff]/35 bg-[#9b8cff]/10 text-[#c5bdff]",
  muted: "border-[#334155] bg-[#1a2331] text-[#aeb9c8]",
};

export function Badge({
  className,
  tone = "muted",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: BadgeTone }) {
  return (
    <span
      className={cn(
        "inline-flex h-6 items-center rounded-md border px-2 text-xs font-medium",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
