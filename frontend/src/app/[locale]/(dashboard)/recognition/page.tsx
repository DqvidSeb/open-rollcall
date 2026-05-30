import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Recognition');
  return { title: t('title') };
}

export default async function RecognitionPage() {
  const t = await getTranslations('Recognition');

  return (
    <PageWrapper title={t('title')}>
      {/* CameraFeed, RecognitionOverlay, CheckInPanel — to be implemented */}
    </PageWrapper>
  );
}
