import { Badge } from "@/components/ui/badge";

export function PageHeader({
  title,
  eyebrow,
  children,
}: {
  title: string;
  eyebrow: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <Badge tone="teal">{eyebrow}</Badge>
        <h1 className="mt-3 text-2xl font-semibold text-[#f5f8ff] sm:text-3xl">
          {title}
        </h1>
      </div>
      {children}
    </div>
  );
}
