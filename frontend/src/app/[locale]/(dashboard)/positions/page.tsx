import { getTranslations } from 'next-intl/server';
import { PositionsPageContent } from '@/features/positions/components/PositionsPageContent';

export async function generateMetadata() {
  const t = await getTranslations('Positions');
  return { title: t('title') };
}

/**
 * Positions page.
 *
 * Mirrors the Departments page layout — toolbar + table sit directly on the
 * page surface, no card wrappers or extra backgrounds.
 */
export default function PositionsPage() {
  return <PositionsPageContent />;
}
