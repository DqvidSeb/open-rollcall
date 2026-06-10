import { getTranslations } from 'next-intl/server';
import { PersonsPageContent } from '@/features/persons/components/PersonsPageContent';

export async function generateMetadata() {
  const t = await getTranslations('Persons');
  return { title: t('title') };
}

/**
 * Persons page.
 *
 * Mirrors the Departments page layout — toolbar + table sit directly
 * on the page surface, no card wrappers or extra backgrounds.
 */
export default function PersonsPage() {
  return <PersonsPageContent />;
}
