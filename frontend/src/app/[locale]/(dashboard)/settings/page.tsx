import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Settings');
  return { title: t('title') };
}

export default async function SettingsPage() {
  const t = await getTranslations('Settings');

  return (
    <PageWrapper title={t('title')}>
      {/* Settings sections — to be implemented */}
    </PageWrapper>
  );
}
