import { ChartCard } from "@/components/charts/chart-card";
import { CategoryBarChart } from "@/components/charts/category-bar-chart";
import { PageHeader } from "@/components/layout/page-header";
import { Reveal } from "@/components/motion/reveal";
import { MerchantTable } from "@/components/tables/merchant-table";
import { TransactionTable } from "@/components/tables/transaction-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getTransactions } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TransactionsPage() {
  const transactions = await getTransactions(25);

  return (
    <>
      <PageHeader title="Transaction Monitoring" eyebrow="Operations" />
      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Reveal>
          <Card>
            <CardHeader>
              <CardTitle>Latest Transactions</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <TransactionTable data={transactions.latest_transactions} />
            </CardContent>
          </Card>
        </Reveal>
        <Reveal delay={0.05}>
          <ChartCard title="Merchant Category Revenue">
            <CategoryBarChart
              data={transactions.merchant_categories}
              labelKey="merchant_category"
              valueKey="revenue"
              color="#19c2a6"
            />
          </ChartCard>
        </Reveal>
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <Reveal delay={0.1}>
          <Card>
            <CardHeader>
              <CardTitle>High Risk Transactions</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <TransactionTable data={transactions.high_risk_transactions} />
            </CardContent>
          </Card>
        </Reveal>
        <Reveal delay={0.15}>
          <Card>
            <CardHeader>
              <CardTitle>Top Merchants</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <MerchantTable data={transactions.top_merchants} />
            </CardContent>
          </Card>
        </Reveal>
      </div>
    </>
  );
}
