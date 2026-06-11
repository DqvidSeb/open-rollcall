import { getTranslations } from 'next-intl/server';
import { AcademicProgramsPageContent } from '@/features/academic-programs/components/AcademicProgramsPageContent';

export async function generateMetadata() {
  const t = await getTranslations('AcademicPrograms');
  return { title: t('title') };
}

/**
 * Academic Programs page.
 *
 * Mirrors the Departments/Positions page layout — toolbar + table sit
 * directly on the page surface, no card wrappers or extra backgrounds.
 */
export default function AcademicProgramsPage() {
  return <AcademicProgramsPageContent />;
}
