// ReportTable — stub, to be implemented
'use client';

import { useTranslations } from 'next-intl';
import { EmptyState } from '@/components/ui/EmptyState';

export function ReportTable() {
  const t = useTranslations('Reports');

  // TODO: wire useReports hook, render table with sortable columns
  return <EmptyState title={t('emptyTitle')} />;
}
