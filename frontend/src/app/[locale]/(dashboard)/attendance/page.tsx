import { getTranslations } from 'next-intl/server';
import { AttendancePageContent } from '@/features/attendance-logs/components/AttendancePageContent';

export async function generateMetadata() {
  const t = await getTranslations('Attendance');
  return { title: t('title') };
}

/**
 * Attendance page.
 *
 * Mirrors the Persons page layout — toolbar + table sit directly
 * on the page surface, no card wrappers or extra backgrounds.
 */
export default function AttendancePage() {
  return <AttendancePageContent />;
}
