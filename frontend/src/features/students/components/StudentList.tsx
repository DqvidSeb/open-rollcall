// StudentList — stub, to be implemented
'use client';

import { useTranslations } from 'next-intl';
import { EmptyState } from '@/components/ui/EmptyState';
import { Spinner } from '@/components/ui/Spinner';

export function StudentList() {
  const t = useTranslations('Students');

  // TODO: wire useStudents hook
  const isLoading = false;
  const isEmpty = true;

  if (isLoading) return <Spinner />;
  if (isEmpty) return <EmptyState title={t('emptyTitle')} description={t('emptyDescription')} />;

  return (
    <div>
      {/* TODO: render StudentCard list or Table */}
    </div>
  );
}
