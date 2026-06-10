import { getTranslations } from 'next-intl/server';
import { DepartmentsPageContent } from '@/features/departments/components/DepartmentsPageContent';

export async function generateMetadata() {
  const t = await getTranslations('Departments');
  return { title: t('title') };
}

/**
 * Departments page.
 *
 * Mirrors the Persons page layout — toolbar + table sit directly on the
 * page surface, no card wrappers or extra backgrounds.
 */
export default function DepartmentsPage() {
  return <DepartmentsPageContent />;
}
