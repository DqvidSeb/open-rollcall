'use client';

import { useTranslations } from 'next-intl';

export function AttendanceToolbar() {
  const t = useTranslations('Attendance');

  return (
    <div className="flex items-center justify-between">
      <h1 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--tbl-primary)', letterSpacing: '-0.01em' }}>
        {t('title')}
      </h1>
    </div>
  );
}
