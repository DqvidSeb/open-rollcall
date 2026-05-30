import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Students');
  return { title: t('title') };
}

export default async function StudentsPage() {
  const t = await getTranslations('Students');

  return (
    <PageWrapper title={t('title')}>
      {/* StudentList, StudentForm — to be implemented */}
    </PageWrapper>
  );
}
