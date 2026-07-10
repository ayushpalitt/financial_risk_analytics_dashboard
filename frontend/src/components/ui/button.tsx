import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Button({
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md border border-[#2c3b50] bg-[#172131] px-3 text-sm font-medium text-[#edf4ff] transition hover:border-[#19c2a6]/55 hover:bg-[#1b293c] disabled:pointer-events-none disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}
