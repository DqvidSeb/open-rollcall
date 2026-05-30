import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Dashboard');
  return { title: t('title') };
}

export default async function DashboardPage() {
  const t = await getTranslations('Dashboard');

  return (
    <PageWrapper title={t('title')}>
      {/* Dashboard overview widgets — to be implemented */}
    </PageWrapper>
  );
}
