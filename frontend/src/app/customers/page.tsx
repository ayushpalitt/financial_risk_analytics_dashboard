import { ChartCard } from "@/components/charts/chart-card";
import { CategoryBarChart } from "@/components/charts/category-bar-chart";
import { PageHeader } from "@/components/layout/page-header";
import { Reveal } from "@/components/motion/reveal";
import { CustomerTable } from "@/components/tables/customer-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCustomers } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CustomersPage() {
  const customers = await getCustomers(25);

  return (
    <>
      <PageHeader title="Customer Analytics" eyebrow="Portfolio Segments" />
      <div className="grid gap-5 xl:grid-cols-2">
        <Reveal>
          <ChartCard title="Segment Revenue">
            <CategoryBarChart
              data={customers.segments}
              labelKey="customer_segment"
              valueKey="revenue"
              color="#9b8cff"
            />
          </ChartCard>
        </Reveal>
        <Reveal delay={0.05}>
          <ChartCard title="Segment Fraud Loss">
            <CategoryBarChart
              data={customers.segments}
              labelKey="customer_segment"
              valueKey="fraud_loss"
              color="#ef5f7a"
            />
          </ChartCard>
        </Reveal>
      </div>
      <Reveal delay={0.1}>
        <Card className="mt-5">
          <CardHeader>
            <CardTitle>Top Customers</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <CustomerTable data={customers.top_customers} />
          </CardContent>
        </Card>
      </Reveal>
    </>
  );
}
