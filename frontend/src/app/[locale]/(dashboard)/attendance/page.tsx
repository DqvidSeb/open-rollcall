import { getTranslations } from 'next-intl/server';
import { PageWrapper } from '@/components/layout/PageWrapper/PageWrapper';

export async function generateMetadata() {
  const t = await getTranslations('Attendance');
  return { title: t('title') };
}

export default async function AttendancePage() {
  const t = await getTranslations('Attendance');

  return (
    <PageWrapper title={t('title')}>
      {/* AttendanceTable, AttendanceFilters — to be implemented */}
    </PageWrapper>
  );
}
