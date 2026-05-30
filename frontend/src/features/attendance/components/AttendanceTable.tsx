// AttendanceTable — stub, to be implemented
'use client';

import { useTranslations } from 'next-intl';
import { Spinner } from '@/components/ui/Spinner';
import { EmptyState } from '@/components/ui/EmptyState';

export function AttendanceTable() {
  const t = useTranslations('Attendance');

  // TODO: wire useAttendance hook
  const isLoading = false;
  const isEmpty = true;

  if (isLoading) return <Spinner />;
  if (isEmpty) return <EmptyState title={t('emptyTitle')} />;

  return (
    <div>
      {/* TODO: Table with columns: student, status, check-in, check-out, confidence */}
    </div>
  );
}
