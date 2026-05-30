// SessionList — stub, to be implemented
'use client';

import { useTranslations } from 'next-intl';
import { Spinner } from '@/components/ui/Spinner';
import { EmptyState } from '@/components/ui/EmptyState';

export function SessionList() {
  const t = useTranslations('Sessions');

  // TODO: wire useSessions hook
  const isLoading = false;
  const isEmpty = true;

  if (isLoading) return <Spinner />;
  if (isEmpty) return <EmptyState title={t('emptyTitle')} description={t('emptyDescription')} />;

  return <div>{/* TODO: render SessionCard list */}</div>;
}
