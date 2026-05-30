import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Reports');
  return { title: t('title') };
}

export default async function ReportsPage() {
  const t = await getTranslations('Reports');

  return (
    <PageWrapper title={t('title')}>
      {/* ReportChart, ReportTable, ReportFilters — to be implemented */}
    </PageWrapper>
  );
}
