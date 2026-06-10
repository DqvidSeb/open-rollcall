import { getLocale } from 'next-intl/server';
import { redirect } from '@/lib/i18n/navigation';

// /:locale → /:locale/dashboard
// Locale-aware: /es redirects to /es/dashboard, / redirects to /dashboard
export default async function LocaleRootPage() {
  const locale = await getLocale();
  redirect({ href: '/dashboard', locale });
}
