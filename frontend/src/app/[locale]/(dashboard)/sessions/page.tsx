import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Sessions');
  return { title: t('title') };
}

export default async function SessionsPage() {
  const t = await getTranslations('Sessions');

  return (
    <PageWrapper title={t('title')}>
      {/* SessionList, SessionForm — to be implemented */}
    </PageWrapper>
  );
}
