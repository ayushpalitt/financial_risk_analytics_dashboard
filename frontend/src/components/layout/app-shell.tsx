"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BrainCircuit,
  FileText,
  Landmark,
  LayoutDashboard,
  ShieldAlert,
  Users,
} from "lucide-react";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: BarChart3 },
  { href: "/fraud", label: "Fraud Analytics", icon: ShieldAlert },
  { href: "/customers", label: "Customer Analytics", icon: Users },
  { href: "/machine-learning", label: "Machine Learning", icon: BrainCircuit },
  { href: "/executive-report", label: "Executive Report", icon: FileText },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-transparent">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[264px] border-r border-[#223044] bg-[#0b1018]/95 px-4 py-5 backdrop-blur xl:block">
        <Link href="/" className="mb-6 flex items-center gap-3 px-2">
          <span className="grid h-10 w-10 place-items-center rounded-lg border border-[#19c2a6]/35 bg-[#19c2a6]/10">
            <Landmark className="h-5 w-5 text-[#7be5d1]" />
          </span>
          <span>
            <span className="block text-sm font-semibold text-[#edf4ff]">
              Financial Risk
            </span>
            <span className="block text-xs text-[#94a3b8]">Analytics</span>
          </span>
        </Link>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-[#9aa8ba] transition",
                  active
                    ? "border border-[#19c2a6]/30 bg-[#172436] text-[#edf4ff]"
                    : "hover:bg-[#111a27] hover:text-[#dce6f5]",
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <header className="sticky top-0 z-20 border-b border-[#223044] bg-[#080b10]/92 px-4 py-3 backdrop-blur xl:hidden">
        <div className="flex items-center gap-2 overflow-x-auto">
          {navItems.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-10 shrink-0 items-center gap-2 rounded-md border px-3 text-xs font-medium",
                  active
                    ? "border-[#19c2a6]/45 bg-[#172436] text-[#edf4ff]"
                    : "border-[#253246] bg-[#101620] text-[#9aa8ba]",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </header>
      <main className="px-4 py-5 sm:px-6 xl:ml-[264px] xl:px-8">
        <div className="mx-auto w-full max-w-[1480px]">{children}</div>
      </main>
    </div>
  );
}
