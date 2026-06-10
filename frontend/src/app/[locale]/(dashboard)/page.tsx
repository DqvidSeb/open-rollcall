import { getLocale } from 'next-intl/server';
import { redirect } from '@/lib/i18n/navigation';

// /:locale (via route group) → redirect to the canonical /dashboard URL
export default async function DashboardGroupRoot() {
  const locale = await getLocale();
  redirect({ href: '/dashboard', locale });
}
