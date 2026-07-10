import { PageHeader } from "@/components/layout/page-header";
import { Reveal } from "@/components/motion/reveal";
import { ReportPanel } from "@/components/report/report-panel";
import { getExecutiveReport } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ExecutiveReportPage() {
  const report = await getExecutiveReport();

  return (
    <>
      <PageHeader title="Executive Report" eyebrow="AI Reporting" />
      <Reveal>
        <ReportPanel initialReport={report} />
      </Reveal>
    </>
  );
}
